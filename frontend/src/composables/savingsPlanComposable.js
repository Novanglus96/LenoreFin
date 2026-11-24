import { computed, ref, watch } from "vue";
import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/vue-query";
import apiClient from "./apiClient";
import { useMainStore } from "@/stores/main";

function fail(error, message) {
  if (error.response?.status === 401) throw error;
  const detail = error.response?.data?.detail ?? error.message;
  useMainStore().showSnackbar(`${message}: ${detail}`, "error");
  throw error;
}

function ok(message) {
  useMainStore().showSnackbar(message, "success");
}

// Everything the plan reads moves when a plan is accepted or a windfall is
// applied. The reminder caches rebuild on the worker a moment later, so the
// plan is fetched again once they have landed.
function invalidateAfterWrite(queryClient) {
  const keys = [
    "savings_plan",
    "buckets",
    "windfall_rules",
    "reminders",
    "accounts",
    "account_forecast",
    "transactions",
    "plan_history",
  ];
  const run = () =>
    keys.forEach(key => queryClient.invalidateQueries({ queryKey: [key] }));
  run();
  setTimeout(run, 4000);
}

function debounced(source, ms) {
  const value = ref(JSON.parse(JSON.stringify(source.value)));
  let timer = null;
  watch(
    source,
    next => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        value.value = JSON.parse(JSON.stringify(next));
      }, ms);
    },
    { deep: true },
  );
  return value;
}

/**
 * The live plan. `window` = ref({start, end}); `edits` = ref({...}).
 * Re-simulates 300ms after the last edit; the previous plan stays on screen
 * meanwhile, so the graphs move rather than blink.
 */
export function useSavingsPlan(window, edits) {
  const queryClient = useQueryClient();
  const settled = debounced(edits, 300);

  const {
    data: plan,
    isLoading,
    isFetching,
    error,
  } = useQuery({
    queryKey: computed(() => [
      "savings_plan",
      window.value.start,
      window.value.end,
      settled.value,
    ]),
    queryFn: async () => {
      try {
        const response = await apiClient.post(
          "/planning/savings-plan/simulate",
          {
            start: window.value.start || null,
            end: window.value.end || null,
            edits: settled.value,
          },
        );
        return response.data;
      } catch (e) {
        if (e.response?.status === 400)
          return { error: e.response.data.detail };
        fail(e, "Plan not calculated");
      }
    },
    placeholderData: keepPreviousData,
  });

  const accept = useMutation({
    mutationFn: async (force = false) => {
      try {
        const response = await apiClient.post("/planning/savings-plan/accept", {
          start: window.value.start || null,
          end: window.value.end || null,
          edits: edits.value,
          force,
        });
        ok("Plan accepted — transfers updated");
        return response.data;
      } catch (e) {
        fail(e, "Plan not accepted");
      }
    },
    onSuccess: () => invalidateAfterWrite(queryClient),
  });

  return {
    plan,
    isLoading,
    isFetching,
    error,
    accept: accept.mutateAsync,
    accepting: accept.isPending,
  };
}

export function usePlanHistory() {
  const queryClient = useQueryClient();
  const { data: acceptances } = useQuery({
    queryKey: ["plan_history", "acceptances"],
    queryFn: async () =>
      (await apiClient.get("/planning/savings-plan/acceptances")).data,
  });
  const { data: windfalls } = useQuery({
    queryKey: ["plan_history", "windfalls"],
    queryFn: async () =>
      (await apiClient.get("/planning/savings-plan/windfalls")).data,
  });
  const revertPlan = useMutation({
    mutationFn: async id => {
      try {
        const r = await apiClient.post(
          `/planning/savings-plan/acceptances/${id}/revert`,
        );
        ok("Plan undone — transfers restored");
        return r.data;
      } catch (e) {
        fail(e, "Plan not undone");
      }
    },
    onSuccess: () => invalidateAfterWrite(queryClient),
  });
  const revertWindfall = useMutation({
    mutationFn: async id => {
      try {
        const r = await apiClient.post(
          `/planning/savings-plan/windfalls/${id}/revert`,
        );
        ok("Windfall undone — transfers deleted");
        return r.data;
      } catch (e) {
        fail(e, "Windfall not undone");
      }
    },
    onSuccess: () => invalidateAfterWrite(queryClient),
  });
  return {
    acceptances,
    windfalls,
    revertPlan: revertPlan.mutateAsync,
    revertWindfall: revertWindfall.mutateAsync,
  };
}

export function useWindfall() {
  const queryClient = useQueryClient();
  const suggest = async amount => {
    try {
      return (
        await apiClient.post("/planning/savings-plan/windfall/suggest", {
          amount,
        })
      ).data;
    } catch (e) {
      fail(e, "No suggestion");
    }
  };
  const apply = useMutation({
    mutationFn: async payload => {
      try {
        const r = await apiClient.post(
          "/planning/savings-plan/windfall/apply",
          payload,
        );
        ok("Windfall applied — pending transfers written");
        return r.data;
      } catch (e) {
        fail(e, "Windfall not applied");
      }
    },
    onSuccess: () => invalidateAfterWrite(queryClient),
  });
  return { suggest, apply: apply.mutateAsync, applying: apply.isPending };
}

export function useBuckets() {
  const queryClient = useQueryClient();
  const { data: buckets, isLoading } = useQuery({
    queryKey: ["buckets"],
    queryFn: async () => (await apiClient.get("/planning/buckets/list")).data,
  });
  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["buckets"] });
    queryClient.invalidateQueries({ queryKey: ["savings_plan"] });
  };
  const save = useMutation({
    mutationFn: async bucket => {
      try {
        const r = bucket.id
          ? await apiClient.put(`/planning/buckets/update/${bucket.id}`, bucket)
          : await apiClient.post("/planning/buckets/create", bucket);
        ok("Bucket saved");
        return r.data;
      } catch (e) {
        fail(e, "Bucket not saved");
      }
    },
    onSuccess: refresh,
  });
  const remove = useMutation({
    mutationFn: async id => {
      try {
        const r = await apiClient.delete(`/planning/buckets/delete/${id}`);
        ok("Bucket deleted");
        return r.data;
      } catch (e) {
        fail(e, "Bucket not deleted");
      }
    },
    onSuccess: refresh,
  });
  return {
    buckets,
    isLoading,
    saveBucket: save.mutateAsync,
    deleteBucket: remove.mutateAsync,
  };
}

export function useWindfallRules() {
  const queryClient = useQueryClient();
  const { data: rules } = useQuery({
    queryKey: ["windfall_rules"],
    queryFn: async () =>
      (await apiClient.get("/planning/windfall-rules/list")).data,
  });
  const refresh = () =>
    queryClient.invalidateQueries({ queryKey: ["windfall_rules"] });
  const save = useMutation({
    mutationFn: async rule => {
      try {
        return rule.id
          ? (
              await apiClient.put(
                `/planning/windfall-rules/update/${rule.id}`,
                rule,
              )
            ).data
          : (await apiClient.post("/planning/windfall-rules/create", rule))
              .data;
      } catch (e) {
        fail(e, "Rule not saved");
      }
    },
    onSuccess: refresh,
  });
  const remove = useMutation({
    mutationFn: async id => {
      try {
        return (await apiClient.delete(`/planning/windfall-rules/delete/${id}`))
          .data;
      } catch (e) {
        fail(e, "Rule not deleted");
      }
    },
    onSuccess: refresh,
  });
  return { rules, saveRule: save.mutateAsync, deleteRule: remove.mutateAsync };
}
