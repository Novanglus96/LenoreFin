<template>
  <span class="animated-icon">
    <component :is="transitions[transition]" mode="out-in">
      <!-- Keying on the icon name is what makes the swap a transition rather
           than an in-place attribute change. -->
      <v-icon :key="icon" :icon="icon" v-bind="$attrs"></v-icon>
    </component>
  </span>
</template>
<script setup>
  import { defineProps } from "vue";
  import { VFadeTransition, VScaleTransition } from "vuetify/components";

  // Attrs land on the inner v-icon (size, color, ...) rather than the wrapper.
  defineOptions({ inheritAttrs: false });

  // Imported rather than resolved from a name string, so a typo is a build
  // error instead of a silently missing icon.
  const transitions = {
    fade: VFadeTransition,
    scale: VScaleTransition,
  };

  defineProps({
    icon: { type: String, required: true },
    // "fade" suits outline/filled pairs of the same glyph; "scale" suits a
    // genuine change of shape.
    // Values are inlined rather than derived from `transitions` above because
    // defineProps is a compile-time macro and cannot see setup scope.
    transition: {
      type: String,
      default: "fade",
      validator: value => ["fade", "scale"].includes(value),
    },
  });
</script>
<style>
  .animated-icon {
    display: inline-flex;
  }

  /* Vuetify's own durations are tuned for panels, not for a button icon that
     toggles under the cursor. out-in runs the two halves back to back, so the
     stock timing reads as lag. Matched by suffix because the generated classes
     are "fade-transition-*" / "scale-transition-*". */
  .animated-icon [class*="-enter-active"],
  .animated-icon [class*="-leave-active"] {
    transition-duration: 0.13s;
  }

  /* createCssTransition, unlike the javascript transitions, does not honour
     reduced motion on its own. */
  @media (prefers-reduced-motion: reduce) {
    .animated-icon [class*="-enter-active"],
    .animated-icon [class*="-leave-active"] {
      transition-duration: 0.01ms;
    }
  }
</style>
