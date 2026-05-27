## [1.5.2-alpha.1](https://github.com/Novanglus96/LenoreFin/compare/v1.5.1...v1.5.2-alpha.1) (2026-05-27)


### Bug Fixes

* favorite accounts projected balance includes reminders and forecasts ([#161](https://github.com/Novanglus96/LenoreFin/issues/161)) ([fa2f61e](https://github.com/Novanglus96/LenoreFin/commit/fa2f61ecd689f16aa7f646567f0c5687c5a1b567))
* per-user favorite accounts and fix widget navigation ([#162](https://github.com/Novanglus96/LenoreFin/issues/162)) ([1207c3c](https://github.com/Novanglus96/LenoreFin/commit/1207c3c54a4671c7e1c65af6a7f7989bbdc4ae5f))

## [1.5.1-alpha.3](https://github.com/Novanglus96/LenoreFin/compare/v1.5.1-alpha.2...v1.5.1-alpha.3) (2026-05-27)


### Bug Fixes

* per-user favorite accounts and fix widget navigation ([#162](https://github.com/Novanglus96/LenoreFin/issues/162)) ([1207c3c](https://github.com/Novanglus96/LenoreFin/commit/1207c3c54a4671c7e1c65af6a7f7989bbdc4ae5f))

## [1.5.1-alpha.2](https://github.com/Novanglus96/LenoreFin/compare/v1.5.1-alpha.1...v1.5.1-alpha.2) (2026-05-27)


### Bug Fixes

* favorite accounts projected balance includes reminders and forecasts ([#161](https://github.com/Novanglus96/LenoreFin/issues/161)) ([fa2f61e](https://github.com/Novanglus96/LenoreFin/commit/fa2f61ecd689f16aa7f646567f0c5687c5a1b567))

## [1.5.1](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0...v1.5.1) (2026-05-26)


### Bug Fixes

* improve ring text readability in yellow budget range ([452eaab](https://github.com/Novanglus96/LenoreFin/commit/452eaab15120dd371573be1a905f1029f26e3edf))
* replace v-progress-circular with inline SVG ring for desktop budget widget ([b6f1ed7](https://github.com/Novanglus96/LenoreFin/commit/b6f1ed79885dcbe4956ab3ae1a0a904ca728ac24))
* restore v-progress-circular and fix color/bg-color collision at yellow threshold ([940a69b](https://github.com/Novanglus96/LenoreFin/commit/940a69bd80794a15a6f732746b6d53a53b1048d4))
* ring and budget text use warning color when over budget ([fa439d0](https://github.com/Novanglus96/LenoreFin/commit/fa439d0ef728f5aab1fbf306a11a4f8b806cb807))
* sort favorite accounts by name and fix desktop budget ring percentage ([2fbaddb](https://github.com/Novanglus96/LenoreFin/commit/2fbaddb53ed1892cc079a85ea42b63d84dc0e1c0))
* use error color for over-budget amounts, label text unchanged ([97fe88e](https://github.com/Novanglus96/LenoreFin/commit/97fe88e23731b6c935f6d5561e435eb3478b9e3b))
* use theme on-surface color for budget ring text ([d9a212d](https://github.com/Novanglus96/LenoreFin/commit/d9a212d87f386f7f2e21b0662d2759dc5031b575))
* use yellow-lighten-4 for budget ring bg track in yellow range for contrast ([63a0113](https://github.com/Novanglus96/LenoreFin/commit/63a01131c2506f0cb3b9583cb12e6513b8dafd46))

## [1.5.1-alpha.1](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0...v1.5.1-alpha.1) (2026-05-26)


### Bug Fixes

* improve ring text readability in yellow budget range ([452eaab](https://github.com/Novanglus96/LenoreFin/commit/452eaab15120dd371573be1a905f1029f26e3edf))
* replace v-progress-circular with inline SVG ring for desktop budget widget ([b6f1ed7](https://github.com/Novanglus96/LenoreFin/commit/b6f1ed79885dcbe4956ab3ae1a0a904ca728ac24))
* restore v-progress-circular and fix color/bg-color collision at yellow threshold ([940a69b](https://github.com/Novanglus96/LenoreFin/commit/940a69bd80794a15a6f732746b6d53a53b1048d4))
* ring and budget text use warning color when over budget ([fa439d0](https://github.com/Novanglus96/LenoreFin/commit/fa439d0ef728f5aab1fbf306a11a4f8b806cb807))
* sort favorite accounts by name and fix desktop budget ring percentage ([2fbaddb](https://github.com/Novanglus96/LenoreFin/commit/2fbaddb53ed1892cc079a85ea42b63d84dc0e1c0))
* use error color for over-budget amounts, label text unchanged ([97fe88e](https://github.com/Novanglus96/LenoreFin/commit/97fe88e23731b6c935f6d5561e435eb3478b9e3b))
* use theme on-surface color for budget ring text ([d9a212d](https://github.com/Novanglus96/LenoreFin/commit/d9a212d87f386f7f2e21b0662d2759dc5031b575))
* use yellow-lighten-4 for budget ring bg track in yellow range for contrast ([63a0113](https://github.com/Novanglus96/LenoreFin/commit/63a01131c2506f0cb3b9583cb12e6513b8dafd46))

# [1.5.0](https://github.com/Novanglus96/LenoreFin/compare/v1.4.2...v1.5.0) (2026-05-26)


### Bug Fixes

* anchor account forecast y-axis to $0 for consistent scale ([0c2efe9](https://github.com/Novanglus96/LenoreFin/commit/0c2efe9bc0795a90a784eddd7ceaf6460be66311))
* auto-add new widget slots to existing user dashboard configs on GET ([84b6e4d](https://github.com/Novanglus96/LenoreFin/commit/84b6e4dbd2b896390b84c8c0fd56a3567f861a1c))
* combined chip display and reminder conversion race condition ([5cb92f1](https://github.com/Novanglus96/LenoreFin/commit/5cb92f125fca04a276284b1de29fdcd90cd6ae85))
* convert note_text to TextField and remove frontend 254-char limit ([#153](https://github.com/Novanglus96/LenoreFin/issues/153)) ([6527395](https://github.com/Novanglus96/LenoreFin/commit/6527395e745401f9a119fe6cbf1ad8eb0186d8ec))
* darken mobile action panel background for better contrast ([22ee69f](https://github.com/Novanglus96/LenoreFin/commit/22ee69fe6cc35432a36da9daad040ee2721343c0))
* import computed from vue not tanstack in dashboardComposable ([507c73e](https://github.com/Novanglus96/LenoreFin/commit/507c73e07a37f6fc5f1d41b80c525f91ef89a9fb))
* parse version tag to determine release type for Reddit announcements ([#145](https://github.com/Novanglus96/LenoreFin/issues/145)) ([f60a690](https://github.com/Novanglus96/LenoreFin/commit/f60a6900dc6e0af2ee99a1b2adc27ad2af237094))
* propagate is_favorite through DTO, service, and mapper layers ([60ef26a](https://github.com/Novanglus96/LenoreFin/commit/60ef26a3448285bd184dd68f4183e5bcc70be939))
* replace combined chip with mdi-layers icon for parent accounts ([8083ec7](https://github.com/Novanglus96/LenoreFin/commit/8083ec7733c02708c7bed09520590ae6f8c0f8a5))
* use v-model:opened on v-list to correctly auto-expand FAVORITES group ([4d6cba2](https://github.com/Novanglus96/LenoreFin/commit/4d6cba290a0cc8927408f4d574df2d73e2e3d38b))


### Features

* add 1st-of-month balance flag to account forecast widget ([#152](https://github.com/Novanglus96/LenoreFin/issues/152)) ([b64f9ce](https://github.com/Novanglus96/LenoreFin/commit/b64f9cec29f2e3e681924fc9ef4b148bae5966c1))
* add account favorites with FAVORITES menu section and header toggle ([98126c0](https://github.com/Novanglus96/LenoreFin/commit/98126c0ed1ce45136f984545003041bcc7b0cd3c))
* add account favorites with star icon and priority sort in menu ([9c8e1bd](https://github.com/Novanglus96/LenoreFin/commit/9c8e1bde47f604006b8c96a51997712773570003))
* add days remaining until budget reset to budget widget ([#154](https://github.com/Novanglus96/LenoreFin/issues/154)) ([9d03371](https://github.com/Novanglus96/LenoreFin/commit/9d03371e1d116a81f496e088dd2a9674bd26cdb1))
* add favorite accounts balance widget to dashboard ([8123cc0](https://github.com/Novanglus96/LenoreFin/commit/8123cc0567167d82fb35b2aa3cc39620d6848039))
* add mobile action bottom sheet on account header name tap ([3143a38](https://github.com/Novanglus96/LenoreFin/commit/3143a38ffac11a1277cefdfccf61530aae751061))
* add toggleable trend line to account forecast widget ([#151](https://github.com/Novanglus96/LenoreFin/issues/151)) ([b1d4c97](https://github.com/Novanglus96/LenoreFin/commit/b1d4c978a9b01275fdc3bb70e9a64f9a75a42713))
* allow all authenticated users to edit dashboard and graph widgets ([2da0999](https://github.com/Novanglus96/LenoreFin/commit/2da09991953db7877d30aed49ffd9d3090ffc6e3))
* auto-expand FAVORITES group on menu load when favorites exist ([3678d69](https://github.com/Novanglus96/LenoreFin/commit/3678d6972ea51f26e8e5fe6c4824146c00c0eb3e))
* move dashboard edit button to app bar, visible only on dashboard route ([46ca5b6](https://github.com/Novanglus96/LenoreFin/commit/46ca5b6fe559254d68ec7f85b58ea78e83b11fc8))
* per-user dashboard widget ordering and visibility ([980b6f2](https://github.com/Novanglus96/LenoreFin/commit/980b6f2f25198d6fd1c13e3696e5479f0b19d115))
* per-user graph widget config (name, type, tag, filters) ([eb2645a](https://github.com/Novanglus96/LenoreFin/commit/eb2645a031375260327aaa6299d9207213e46205))
* per-user reports with optional sharing ([#157](https://github.com/Novanglus96/LenoreFin/issues/157)) ([991b3e4](https://github.com/Novanglus96/LenoreFin/commit/991b3e4506b2ca6162244323ecc9cff2aeb38ad2))
* replace bottom sheet with inline expand panel for mobile account actions ([3e13222](https://github.com/Novanglus96/LenoreFin/commit/3e13222d0272a3d0a3cde276c165ec469d7fe45c))

# [1.5.0-alpha.7](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0-alpha.6...v1.5.0-alpha.7) (2026-05-26)


### Features

* per-user reports with optional sharing ([#157](https://github.com/Novanglus96/LenoreFin/issues/157)) ([991b3e4](https://github.com/Novanglus96/LenoreFin/commit/991b3e4506b2ca6162244323ecc9cff2aeb38ad2))

# [1.5.0-alpha.6](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0-alpha.5...v1.5.0-alpha.6) (2026-05-26)


### Bug Fixes

* auto-add new widget slots to existing user dashboard configs on GET ([84b6e4d](https://github.com/Novanglus96/LenoreFin/commit/84b6e4dbd2b896390b84c8c0fd56a3567f861a1c))
* import computed from vue not tanstack in dashboardComposable ([507c73e](https://github.com/Novanglus96/LenoreFin/commit/507c73e07a37f6fc5f1d41b80c525f91ef89a9fb))


### Features

* add favorite accounts balance widget to dashboard ([8123cc0](https://github.com/Novanglus96/LenoreFin/commit/8123cc0567167d82fb35b2aa3cc39620d6848039))
* allow all authenticated users to edit dashboard and graph widgets ([2da0999](https://github.com/Novanglus96/LenoreFin/commit/2da09991953db7877d30aed49ffd9d3090ffc6e3))
* move dashboard edit button to app bar, visible only on dashboard route ([46ca5b6](https://github.com/Novanglus96/LenoreFin/commit/46ca5b6fe559254d68ec7f85b58ea78e83b11fc8))
* per-user dashboard widget ordering and visibility ([980b6f2](https://github.com/Novanglus96/LenoreFin/commit/980b6f2f25198d6fd1c13e3696e5479f0b19d115))
* per-user graph widget config (name, type, tag, filters) ([eb2645a](https://github.com/Novanglus96/LenoreFin/commit/eb2645a031375260327aaa6299d9207213e46205))

# [1.5.0-alpha.5](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0-alpha.4...v1.5.0-alpha.5) (2026-05-26)


### Bug Fixes

* darken mobile action panel background for better contrast ([22ee69f](https://github.com/Novanglus96/LenoreFin/commit/22ee69fe6cc35432a36da9daad040ee2721343c0))
* propagate is_favorite through DTO, service, and mapper layers ([60ef26a](https://github.com/Novanglus96/LenoreFin/commit/60ef26a3448285bd184dd68f4183e5bcc70be939))
* replace combined chip with mdi-layers icon for parent accounts ([8083ec7](https://github.com/Novanglus96/LenoreFin/commit/8083ec7733c02708c7bed09520590ae6f8c0f8a5))
* use v-model:opened on v-list to correctly auto-expand FAVORITES group ([4d6cba2](https://github.com/Novanglus96/LenoreFin/commit/4d6cba290a0cc8927408f4d574df2d73e2e3d38b))


### Features

* add account favorites with FAVORITES menu section and header toggle ([98126c0](https://github.com/Novanglus96/LenoreFin/commit/98126c0ed1ce45136f984545003041bcc7b0cd3c))
* add account favorites with star icon and priority sort in menu ([9c8e1bd](https://github.com/Novanglus96/LenoreFin/commit/9c8e1bde47f604006b8c96a51997712773570003))
* add mobile action bottom sheet on account header name tap ([3143a38](https://github.com/Novanglus96/LenoreFin/commit/3143a38ffac11a1277cefdfccf61530aae751061))
* auto-expand FAVORITES group on menu load when favorites exist ([3678d69](https://github.com/Novanglus96/LenoreFin/commit/3678d6972ea51f26e8e5fe6c4824146c00c0eb3e))
* replace bottom sheet with inline expand panel for mobile account actions ([3e13222](https://github.com/Novanglus96/LenoreFin/commit/3e13222d0272a3d0a3cde276c165ec469d7fe45c))

# [1.5.0-alpha.4](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0-alpha.3...v1.5.0-alpha.4) (2026-05-26)


### Features

* add days remaining until budget reset to budget widget ([#154](https://github.com/Novanglus96/LenoreFin/issues/154)) ([9d03371](https://github.com/Novanglus96/LenoreFin/commit/9d03371e1d116a81f496e088dd2a9674bd26cdb1))

# [1.5.0-alpha.3](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0-alpha.2...v1.5.0-alpha.3) (2026-05-26)


### Bug Fixes

* convert note_text to TextField and remove frontend 254-char limit ([#153](https://github.com/Novanglus96/LenoreFin/issues/153)) ([6527395](https://github.com/Novanglus96/LenoreFin/commit/6527395e745401f9a119fe6cbf1ad8eb0186d8ec))

# [1.5.0-alpha.2](https://github.com/Novanglus96/LenoreFin/compare/v1.5.0-alpha.1...v1.5.0-alpha.2) (2026-05-26)


### Features

* add 1st-of-month balance flag to account forecast widget ([#152](https://github.com/Novanglus96/LenoreFin/issues/152)) ([b64f9ce](https://github.com/Novanglus96/LenoreFin/commit/b64f9cec29f2e3e681924fc9ef4b148bae5966c1))

# [1.5.0-alpha.1](https://github.com/Novanglus96/LenoreFin/compare/v1.4.3-alpha.1...v1.5.0-alpha.1) (2026-05-26)


### Features

* add toggleable trend line to account forecast widget ([#151](https://github.com/Novanglus96/LenoreFin/issues/151)) ([b1d4c97](https://github.com/Novanglus96/LenoreFin/commit/b1d4c978a9b01275fdc3bb70e9a64f9a75a42713))

## [1.4.3-alpha.1](https://github.com/Novanglus96/LenoreFin/compare/v1.4.2...v1.4.3-alpha.1) (2026-05-22)


### Bug Fixes

* anchor account forecast y-axis to $0 for consistent scale ([0c2efe9](https://github.com/Novanglus96/LenoreFin/commit/0c2efe9bc0795a90a784eddd7ceaf6460be66311))
* combined chip display and reminder conversion race condition ([5cb92f1](https://github.com/Novanglus96/LenoreFin/commit/5cb92f125fca04a276284b1de29fdcd90cd6ae85))
* parse version tag to determine release type for Reddit announcements ([#145](https://github.com/Novanglus96/LenoreFin/issues/145)) ([f60a690](https://github.com/Novanglus96/LenoreFin/commit/f60a6900dc6e0af2ee99a1b2adc27ad2af237094))

# [1.4.0-alpha.47](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.46...v1.4.0-alpha.47) (2026-05-22)
## [1.4.2](https://github.com/Novanglus96/LenoreFin/compare/v1.4.1...v1.4.2) (2026-05-22)


### Bug Fixes

* anchor account forecast y-axis to $0 for consistent scale ([0c2efe9](https://github.com/Novanglus96/LenoreFin/commit/0c2efe9bc0795a90a784eddd7ceaf6460be66311))
* combined chip display and reminder conversion race condition ([5cb92f1](https://github.com/Novanglus96/LenoreFin/commit/5cb92f125fca04a276284b1de29fdcd90cd6ae85))

# [1.4.0-alpha.46](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.45...v1.4.0-alpha.46) (2026-05-22)
* anchor account forecast y-axis to $0 for consistent scale ([a306226](https://github.com/Novanglus96/LenoreFin/commit/a30622601d4a9b739b3bbbf4bfe2289a7d8de7ed))
* combined chip display and reminder conversion race condition ([b9507de](https://github.com/Novanglus96/LenoreFin/commit/b9507deb1d25e83cea5ef8d33b01922df97cc9c2))

## [1.4.1](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0...v1.4.1) (2026-05-22)


### Bug Fixes

* parse version tag to determine release type for Reddit announcements ([#145](https://github.com/Novanglus96/LenoreFin/issues/145)) ([f60a690](https://github.com/Novanglus96/LenoreFin/commit/f60a6900dc6e0af2ee99a1b2adc27ad2af237094))
* restore UserAdmin fieldsets by correcting MRO in RestrictedUserAdmin ([#147](https://github.com/Novanglus96/LenoreFin/issues/147)) ([fb1b165](https://github.com/Novanglus96/LenoreFin/commit/fb1b1658b45887be2287b6889b31bcf6b9f40737))

# [1.4.0](https://github.com/Novanglus96/LenoreFin/compare/v1.3.1...v1.4.0) (2026-05-22)


### Bug Fixes

* auth post-login bugs — superuser group, logout, 401 race ([#66](https://github.com/Novanglus96/LenoreFin/issues/66)) ([b2db4a0](https://github.com/Novanglus96/LenoreFin/commit/b2db4a0b2e8cd8be699b1e4d43a8826e42dfaf1d))
* backup restore — reminders 500, bank logos, expense graph, cache rebuild ([#132](https://github.com/Novanglus96/LenoreFin/issues/132)) ([5a3ea71](https://github.com/Novanglus96/LenoreFin/commit/5a3ea71c7cab357a44524a7264aafae4f8a32087)), closes [#92](https://github.com/Novanglus96/LenoreFin/issues/92)
* calculator cancel button and inline docstrings ([#131](https://github.com/Novanglus96/LenoreFin/issues/131)) ([82c9e3e](https://github.com/Novanglus96/LenoreFin/commit/82c9e3e5237a19ea57692cd77a1995e7327e84b3))
* consolidate mobile form twins into single responsive components ([#104](https://github.com/Novanglus96/LenoreFin/issues/104)) ([bf3460b](https://github.com/Novanglus96/LenoreFin/commit/bf3460b18b7e8a596229c109f53fa9fc7263033c))
* coordinate version banner reload with service worker lifecycle ([#143](https://github.com/Novanglus96/LenoreFin/issues/143)) ([0cf1624](https://github.com/Novanglus96/LenoreFin/commit/0cf1624772be1830275426387b50cf0811e733f8))
* correct budget percentage calculation when rollover produces negative starting balance ([#67](https://github.com/Novanglus96/LenoreFin/issues/67)) ([e4ffc23](https://github.com/Novanglus96/LenoreFin/commit/e4ffc23c83594ee7496fa3f7bbbd4082da7fd930))
* correct budget percentage calculation when rollover produces negative starting balance ([#68](https://github.com/Novanglus96/LenoreFin/issues/68)) ([29e942a](https://github.com/Novanglus96/LenoreFin/commit/29e942a268fd474bbc6dbad20f6e1cf2919a0550))
* correct CC payment calculation, deduplication, and cache invalidation ([#80](https://github.com/Novanglus96/LenoreFin/issues/80)) ([6f4a745](https://github.com/Novanglus96/LenoreFin/commit/6f4a745e764406cf8aa246a48cc22e1c40dede21))
* correct GITHUB_ENV writes in Compute project identifiers step ([#75](https://github.com/Novanglus96/LenoreFin/issues/75)) ([3000669](https://github.com/Novanglus96/LenoreFin/commit/3000669291114b5d5da816863bb4faf20723f4b1))
* declare __OPT_FEATURES__ as ESLint global to fix production build ([#111](https://github.com/Novanglus96/LenoreFin/issues/111)) ([6995913](https://github.com/Novanglus96/LenoreFin/commit/699591343113d5b840af7c784f3b78f1d0cea31e))
* differentiate system vs user tag icon colors ([#101](https://github.com/Novanglus96/LenoreFin/issues/101)) ([bb64c02](https://github.com/Novanglus96/LenoreFin/commit/bb64c02f1936556a89c019b6bdbb5db6b1e1ddff))
* disabling an account no longer wipes open_date ([#74](https://github.com/Novanglus96/LenoreFin/issues/74)) ([4dec53a](https://github.com/Novanglus96/LenoreFin/commit/4dec53af855c81f82fa762abb35e11d132b79338))
* forecast graph cache collision and backup timestamp timezone ([#136](https://github.com/Novanglus96/LenoreFin/issues/136)) ([2944d1a](https://github.com/Novanglus96/LenoreFin/commit/2944d1a6f460cae781d8da590c04d72b0c369efe))
* guard attachment_count annotation to Transaction queryset only ([#108](https://github.com/Novanglus96/LenoreFin/issues/108)) ([0057240](https://github.com/Novanglus96/LenoreFin/commit/00572406c3cb3cbf2e0d1fafc9097a24cf5342f5))
* migrate transaction forms to vee-validate + Yup validation ([#97](https://github.com/Novanglus96/LenoreFin/issues/97)) ([9ac358b](https://github.com/Novanglus96/LenoreFin/commit/9ac358b89ccbf8fee311f243eab4bc631a56813c))
* missing closing bracket on v-dialog tag in ReminderForm ([#105](https://github.com/Novanglus96/LenoreFin/issues/105)) ([16adb8b](https://github.com/Novanglus96/LenoreFin/commit/16adb8b8c64f43072c4233610d1e30299c7442e3))
* mobile menu admin links, auth gating, and version placement ([#116](https://github.com/Novanglus96/LenoreFin/issues/116)) ([a78c83f](https://github.com/Novanglus96/LenoreFin/commit/a78c83fdaa65469559c301be8bee0e5ea9c84136))
* mobile overflow, nav icon sizing, and logs polish ([f7f5db2](https://github.com/Novanglus96/LenoreFin/commit/f7f5db27e61295c2309360dc0b44f17a69ea2367))
* patch frontend security vulnerabilities and update patch/minor deps ([#114](https://github.com/Novanglus96/LenoreFin/issues/114)) ([6b85e9f](https://github.com/Novanglus96/LenoreFin/commit/6b85e9f4a87af58549734b81a17c30db64703c7d))
* Phase 7b cleanup — nav, tag filtering, and admin polish ([#122](https://github.com/Novanglus96/LenoreFin/issues/122)) ([2a2548b](https://github.com/Novanglus96/LenoreFin/commit/2a2548bc4aea5157e5222d00ff1e9d6a8b691e2c))
* post-restore discrepancies — schema nullability, custom repeats, CC forecast ([#134](https://github.com/Novanglus96/LenoreFin/issues/134)) ([4007efb](https://github.com/Novanglus96/LenoreFin/commit/4007efb8fbe3453d41b99096939441f918ec9f24))
* raise Workbox precache limit to 3 MiB for ApexCharts bundle ([#138](https://github.com/Novanglus96/LenoreFin/issues/138)) ([5921a86](https://github.com/Novanglus96/LenoreFin/commit/5921a863d76d4db9e2c6adc308481fe14948a9b2))
* read VITE_OPT_FEATURES from process.env instead of .env file ([#109](https://github.com/Novanglus96/LenoreFin/issues/109)) ([057f2a5](https://github.com/Novanglus96/LenoreFin/commit/057f2a52c5511724f17b1e1a10b4728cf46f32ea))
* reminder conversion now updates start_date to next non-excluded date ([#76](https://github.com/Novanglus96/LenoreFin/issues/76)) ([7d6b4ab](https://github.com/Novanglus96/LenoreFin/commit/7d6b4ab1ba1bc2906378041c8c186a3e9dfedb08))
* remove forecast timeframe options beyond 1 year ([#125](https://github.com/Novanglus96/LenoreFin/issues/125)) ([b3cc9d9](https://github.com/Novanglus96/LenoreFin/commit/b3cc9d9e31bddd39d1c57d5d2f81eb98269f6743))
* replace django-jazzmin with django-unfold for admin theming ([#124](https://github.com/Novanglus96/LenoreFin/issues/124)) ([db90547](https://github.com/Novanglus96/LenoreFin/commit/db905470708264418571c70cfc00fe75f77837b7)), closes [#06966](https://github.com/Novanglus96/LenoreFin/issues/06966)
* resolve three Phase 2b bugs found during CC interest testing ([#84](https://github.com/Novanglus96/LenoreFin/issues/84)) ([d325509](https://github.com/Novanglus96/LenoreFin/commit/d325509e00d07b87783968f9561ace662226fc20))
* restore csrf=False on auth classes broken by django-ninja 1.6 upgrade ([#77](https://github.com/Novanglus96/LenoreFin/issues/77)) ([c8f5edd](https://github.com/Novanglus96/LenoreFin/commit/c8f5eddfac98912661ddb4e2c6c54d38deb12367))
* show paycheck gross discrepancy amount in validation error ([#99](https://github.com/Novanglus96/LenoreFin/issues/99)) ([7dac50d](https://github.com/Novanglus96/LenoreFin/commit/7dac50d54687a18070b841a5efcefe17d2f39c0d))
* suppress signals during restore and deepen tag select_related ([#135](https://github.com/Novanglus96/LenoreFin/issues/135)) ([38a0b9f](https://github.com/Novanglus96/LenoreFin/commit/38a0b9f8f21d6e8926026fb7294160b7e973f2d6))
* surface attachment_count on TransactionOut to show paperclip icon ([#107](https://github.com/Novanglus96/LenoreFin/issues/107)) ([4aaa588](https://github.com/Novanglus96/LenoreFin/commit/4aaa5888ed30a2d1abf2f586cff96ccb5294f843))
* test branch protection bypass for semantic-release version commit ([4d635d5](https://github.com/Novanglus96/LenoreFin/commit/4d635d51f72d214c617507df9d27f818fbc1ed1a))
* use plain global constant for opt features flag ([#110](https://github.com/Novanglus96/LenoreFin/issues/110)) ([e6afd23](https://github.com/Novanglus96/LenoreFin/commit/e6afd23ec21af0cd8383d7757ded5616bbf73b9c))


### Features

* add bank logos to account header, menu, and forecast selector ([#128](https://github.com/Novanglus96/LenoreFin/issues/128)) ([7fe0448](https://github.com/Novanglus96/LenoreFin/commit/7fe0448ccd6f19b3e7c5ebad967a17b3088513ff))
* add bank logos to account menu and header ([#127](https://github.com/Novanglus96/LenoreFin/issues/127)) ([66148cc](https://github.com/Novanglus96/LenoreFin/commit/66148cc284230022c29bd27dd8533e977fba8413))
* add custom JSON backup/restore system with scheduled automation ([#92](https://github.com/Novanglus96/LenoreFin/issues/92)) ([b8d7bc2](https://github.com/Novanglus96/LenoreFin/commit/b8d7bc2f801a426eb9d16bad10dd15f68e49aeb3))
* add edit/delete for tags, blocking is_system tags ([#100](https://github.com/Novanglus96/LenoreFin/issues/100)) ([54a235b](https://github.com/Novanglus96/LenoreFin/commit/54a235b3def23fe38fb5fa73c6eee34122a2e9fb))
* add file attachments to transactions ([#106](https://github.com/Novanglus96/LenoreFin/issues/106)) ([970f82d](https://github.com/Novanglus96/LenoreFin/commit/970f82de843a814b331f39a02cc43918e997e6b9))
* add is_system and slug fields to system-seeded models ([#78](https://github.com/Novanglus96/LenoreFin/issues/78)) ([ca652a8](https://github.com/Novanglus96/LenoreFin/commit/ca652a8981b4e04c9bbb318071ff5d11b40454b4))
* add parent account support with combined balance and interest forecasting ([#95](https://github.com/Novanglus96/LenoreFin/issues/95)) ([56c6128](https://github.com/Novanglus96/LenoreFin/commit/56c612871e9e18282a142ece432fd3e002610da8))
* add payee management — CRUD view and inline add from transaction form ([#98](https://github.com/Novanglus96/LenoreFin/issues/98)) ([8b75e5f](https://github.com/Novanglus96/LenoreFin/commit/8b75e5f6ac3c9c686785801eb879fc92427b3489))
* add session-based auth with group permissions (Full Access / Readonly) ([#65](https://github.com/Novanglus96/LenoreFin/issues/65)) ([85c6e07](https://github.com/Novanglus96/LenoreFin/commit/85c6e07db5a6138f5673b765f2bb2156f9195662))
* add transaction filtering by description, status, type, and tag ([#126](https://github.com/Novanglus96/LenoreFin/issues/126)) ([2cf54df](https://github.com/Novanglus96/LenoreFin/commit/2cf54df871125f3f98188d3f5147f151ef466d01))
* add VITE_OPT_FEATURES flag to gate optional planning menu items ([#102](https://github.com/Novanglus96/LenoreFin/issues/102)) ([59e8fac](https://github.com/Novanglus96/LenoreFin/commit/59e8fac28a1037d5432615da43b52717b8beddf3))
* consolidate production containers into single app image ([#120](https://github.com/Novanglus96/LenoreFin/issues/120)) ([66a5e75](https://github.com/Novanglus96/LenoreFin/commit/66a5e7564655a13c907bc51def1ba6e79b1884e9))
* custom reporting — Phase 6 ([#118](https://github.com/Novanglus96/LenoreFin/issues/118)) ([acd886f](https://github.com/Novanglus96/LenoreFin/commit/acd886feb4fa49da4ba4cfa256367d18ed8a88b2))
* highlight lowest post-today balance on account forecast chart ([#142](https://github.com/Novanglus96/LenoreFin/issues/142)) ([a3c22bc](https://github.com/Novanglus96/LenoreFin/commit/a3c22bcb28854c7cf6a92591721169991aa513ab))
* improve retirement forecast with area chart and transaction list ([#93](https://github.com/Novanglus96/LenoreFin/issues/93)) ([c1e7ed4](https://github.com/Novanglus96/LenoreFin/commit/c1e7ed4683197b305a56fef8de37b968a5d9e481))
* logging improvements — traceback capture, log viewer, bundle download ([#115](https://github.com/Novanglus96/LenoreFin/issues/115)) ([42e7594](https://github.com/Novanglus96/LenoreFin/commit/42e7594fbb6c0ae6fa77836e87d14e3aae78bdd2))
* migrate all charts from Chart.js to ApexCharts ([#137](https://github.com/Novanglus96/LenoreFin/issues/137)) ([4fe9056](https://github.com/Novanglus96/LenoreFin/commit/4fe9056fede87364ca600ce769b3e71434fc8592)), closes [#034a45](https://github.com/Novanglus96/LenoreFin/issues/034a45) [#88b3b0](https://github.com/Novanglus96/LenoreFin/issues/88b3b0)
* migrate to Django 5.2 LTS ([#113](https://github.com/Novanglus96/LenoreFin/issues/113)) ([0dcd127](https://github.com/Novanglus96/LenoreFin/commit/0dcd127f9d5dae741fd3d32f2cf1672354c25aae))
* PWA offline mode — readonly when offline, service worker, install support ([#121](https://github.com/Novanglus96/LenoreFin/issues/121)) ([168c9b7](https://github.com/Novanglus96/LenoreFin/commit/168c9b746f09b8423bd77e400f8097f4eb573125)), closes [#06966](https://github.com/Novanglus96/LenoreFin/issues/06966)
* scheduled daily pruning of django-q2 task history ([#85](https://github.com/Novanglus96/LenoreFin/issues/85)) ([f711f21](https://github.com/Novanglus96/LenoreFin/commit/f711f217e989e32fe7714af729a6cd17e180c955))
* version check on backup/restore with warning on mismatch ([b331a3c](https://github.com/Novanglus96/LenoreFin/commit/b331a3c9934d2bf3e619420f4d02549346987d8a))
* wire up widget edit form for dashboard pie chart widgets ([#103](https://github.com/Novanglus96/LenoreFin/issues/103)) ([8f1a080](https://github.com/Novanglus96/LenoreFin/commit/8f1a0802841173b48f1e1feb603478afbe28f6f4))


### Performance Improvements

* async forecast cache updates, N+1 elimination, and query invalidation fixes ([#94](https://github.com/Novanglus96/LenoreFin/issues/94)) ([2b44818](https://github.com/Novanglus96/LenoreFin/commit/2b44818efeb2474261fa93e3b919735b550ba887))

# [1.4.0-alpha.45](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.44...v1.4.0-alpha.45) (2026-05-22)


### Bug Fixes

* coordinate version banner reload with service worker lifecycle ([#143](https://github.com/Novanglus96/LenoreFin/issues/143)) ([0cf1624](https://github.com/Novanglus96/LenoreFin/commit/0cf1624772be1830275426387b50cf0811e733f8))

# [1.4.0-alpha.44](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.43...v1.4.0-alpha.44) (2026-05-22)


### Bug Fixes

* test branch protection bypass for semantic-release version commit ([4d635d5](https://github.com/Novanglus96/LenoreFin/commit/4d635d51f72d214c617507df9d27f818fbc1ed1a))


### Features

* highlight lowest post-today balance on account forecast chart ([#142](https://github.com/Novanglus96/LenoreFin/issues/142)) ([a3c22bc](https://github.com/Novanglus96/LenoreFin/commit/a3c22bcb28854c7cf6a92591721169991aa513ab))

# [1.4.0-alpha.43](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.42...v1.4.0-alpha.43) (2026-05-22)


### Bug Fixes

* mobile overflow, nav icon sizing, and logs polish ([f7f5db2](https://github.com/Novanglus96/LenoreFin/commit/f7f5db27e61295c2309360dc0b44f17a69ea2367))

# [1.4.0-alpha.42](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.41...v1.4.0-alpha.42) (2026-05-21)


### Bug Fixes

* raise Workbox precache limit to 3 MiB for ApexCharts bundle ([#138](https://github.com/Novanglus96/LenoreFin/issues/138)) ([5921a86](https://github.com/Novanglus96/LenoreFin/commit/5921a863d76d4db9e2c6adc308481fe14948a9b2))

# [1.4.0-alpha.41](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.40...v1.4.0-alpha.41) (2026-05-21)


### Features

* migrate all charts from Chart.js to ApexCharts ([#137](https://github.com/Novanglus96/LenoreFin/issues/137)) ([4fe9056](https://github.com/Novanglus96/LenoreFin/commit/4fe9056fede87364ca600ce769b3e71434fc8592)), closes [#034a45](https://github.com/Novanglus96/LenoreFin/issues/034a45) [#88b3b0](https://github.com/Novanglus96/LenoreFin/issues/88b3b0)

# [1.4.0-alpha.40](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.39...v1.4.0-alpha.40) (2026-05-21)


### Bug Fixes

* forecast graph cache collision and backup timestamp timezone ([#136](https://github.com/Novanglus96/LenoreFin/issues/136)) ([2944d1a](https://github.com/Novanglus96/LenoreFin/commit/2944d1a6f460cae781d8da590c04d72b0c369efe))

# [1.4.0-alpha.39](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.38...v1.4.0-alpha.39) (2026-05-21)


### Bug Fixes

* suppress signals during restore and deepen tag select_related ([#135](https://github.com/Novanglus96/LenoreFin/issues/135)) ([38a0b9f](https://github.com/Novanglus96/LenoreFin/commit/38a0b9f8f21d6e8926026fb7294160b7e973f2d6))

# [1.4.0-alpha.38](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.37...v1.4.0-alpha.38) (2026-05-21)


### Bug Fixes

* post-restore discrepancies — schema nullability, custom repeats, CC forecast ([#134](https://github.com/Novanglus96/LenoreFin/issues/134)) ([4007efb](https://github.com/Novanglus96/LenoreFin/commit/4007efb8fbe3453d41b99096939441f918ec9f24))

# [1.4.0-alpha.37](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.36...v1.4.0-alpha.37) (2026-05-21)


### Features

* version check on backup/restore with warning on mismatch ([b331a3c](https://github.com/Novanglus96/LenoreFin/commit/b331a3c9934d2bf3e619420f4d02549346987d8a))

# [1.4.0-alpha.36](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.35...v1.4.0-alpha.36) (2026-05-21)


### Bug Fixes

* backup restore — reminders 500, bank logos, expense graph, cache rebuild ([#132](https://github.com/Novanglus96/LenoreFin/issues/132)) ([5a3ea71](https://github.com/Novanglus96/LenoreFin/commit/5a3ea71c7cab357a44524a7264aafae4f8a32087)), closes [#92](https://github.com/Novanglus96/LenoreFin/issues/92)

# [1.4.0-alpha.35](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.34...v1.4.0-alpha.35) (2026-05-21)


### Bug Fixes

* calculator cancel button and inline docstrings ([#131](https://github.com/Novanglus96/LenoreFin/issues/131)) ([82c9e3e](https://github.com/Novanglus96/LenoreFin/commit/82c9e3e5237a19ea57692cd77a1995e7327e84b3))

# [1.4.0-alpha.34](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.33...v1.4.0-alpha.34) (2026-05-20)


### Features

* add bank logos to account header, menu, and forecast selector ([#128](https://github.com/Novanglus96/LenoreFin/issues/128)) ([7fe0448](https://github.com/Novanglus96/LenoreFin/commit/7fe0448ccd6f19b3e7c5ebad967a17b3088513ff))

# [1.4.0-alpha.33](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.32...v1.4.0-alpha.33) (2026-05-20)


### Features

* add bank logos to account menu and header ([#127](https://github.com/Novanglus96/LenoreFin/issues/127)) ([66148cc](https://github.com/Novanglus96/LenoreFin/commit/66148cc284230022c29bd27dd8533e977fba8413))

# [1.4.0-alpha.32](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.31...v1.4.0-alpha.32) (2026-05-20)


### Features

* add transaction filtering by description, status, type, and tag ([#126](https://github.com/Novanglus96/LenoreFin/issues/126)) ([2cf54df](https://github.com/Novanglus96/LenoreFin/commit/2cf54df871125f3f98188d3f5147f151ef466d01))

# [1.4.0-alpha.31](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.30...v1.4.0-alpha.31) (2026-05-20)


### Bug Fixes

* remove forecast timeframe options beyond 1 year ([#125](https://github.com/Novanglus96/LenoreFin/issues/125)) ([b3cc9d9](https://github.com/Novanglus96/LenoreFin/commit/b3cc9d9e31bddd39d1c57d5d2f81eb98269f6743))

# [1.4.0-alpha.30](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.29...v1.4.0-alpha.30) (2026-05-20)


### Bug Fixes

* replace django-jazzmin with django-unfold for admin theming ([#124](https://github.com/Novanglus96/LenoreFin/issues/124)) ([db90547](https://github.com/Novanglus96/LenoreFin/commit/db905470708264418571c70cfc00fe75f77837b7)), closes [#06966](https://github.com/Novanglus96/LenoreFin/issues/06966)

# [1.4.0-alpha.29](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.28...v1.4.0-alpha.29) (2026-05-20)


### Bug Fixes

* Phase 7b cleanup — nav, tag filtering, and admin polish ([#122](https://github.com/Novanglus96/LenoreFin/issues/122)) ([2a2548b](https://github.com/Novanglus96/LenoreFin/commit/2a2548bc4aea5157e5222d00ff1e9d6a8b691e2c))

# [1.4.0-alpha.28](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.27...v1.4.0-alpha.28) (2026-05-19)


### Features

* PWA offline mode — readonly when offline, service worker, install support ([#121](https://github.com/Novanglus96/LenoreFin/issues/121)) ([168c9b7](https://github.com/Novanglus96/LenoreFin/commit/168c9b746f09b8423bd77e400f8097f4eb573125)), closes [#06966](https://github.com/Novanglus96/LenoreFin/issues/06966)

# [1.4.0-alpha.27](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.26...v1.4.0-alpha.27) (2026-05-19)


### Features

* consolidate production containers into single app image ([#120](https://github.com/Novanglus96/LenoreFin/issues/120)) ([66a5e75](https://github.com/Novanglus96/LenoreFin/commit/66a5e7564655a13c907bc51def1ba6e79b1884e9))

# [1.4.0-alpha.26](https://github.com/Novanglus96/LenoreFin/compare/v1.4.0-alpha.25...v1.4.0-alpha.26) (2026-05-19)


### Bug Fixes

* correct CC statement cycle start date and due/pay date sequencing ([#119](https://github.com/Novanglus96/LenoreFin/issues/119)) ([cc2e531](https://github.com/Novanglus96/LenoreFin/commit/cc2e53188378fe202a3dabd7c4d531b45beaf5ed))

## [1.3.1](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0...v1.3.1) (2026-05-19)


### Bug Fixes

* correct CC statement cycle start date and due/pay date sequencing ([#119](https://github.com/Novanglus96/LenoreFin/issues/119)) ([cc2e531](https://github.com/Novanglus96/LenoreFin/commit/cc2e53188378fe202a3dabd7c4d531b45beaf5ed))

# [1.3.0](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0...v1.3.0) (2026-05-12)


### Features

* savings and investment account interest forecasting ([#87](https://github.com/Novanglus96/LenoreFin/issues/87)) ([3fbd5d4](https://github.com/Novanglus96/LenoreFin/commit/3fbd5d4d0e25733fee949a3da741b2d9ad6d1e83)), closes [#65](https://github.com/Novanglus96/LenoreFin/issues/65) [#66](https://github.com/Novanglus96/LenoreFin/issues/66)

# [1.3.0-alpha.11](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.10...v1.3.0-alpha.11) (2026-05-12)


### Features

* scheduled daily pruning of django-q2 task history ([#85](https://github.com/Novanglus96/LenoreFin/issues/85)) ([f711f21](https://github.com/Novanglus96/LenoreFin/commit/f711f217e989e32fe7714af729a6cd17e180c955))

# [1.3.0-alpha.10](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.9...v1.3.0-alpha.10) (2026-05-12)


### Bug Fixes

* resolve three Phase 2b bugs found during CC interest testing ([#84](https://github.com/Novanglus96/LenoreFin/issues/84)) ([d325509](https://github.com/Novanglus96/LenoreFin/commit/d325509e00d07b87783968f9561ace662226fc20))

# [1.3.0-alpha.9](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.8...v1.3.0-alpha.9) (2026-05-11)


### Bug Fixes

* correct CC payment calculation, deduplication, and cache invalidation ([#80](https://github.com/Novanglus96/LenoreFin/issues/80)) ([6f4a745](https://github.com/Novanglus96/LenoreFin/commit/6f4a745e764406cf8aa246a48cc22e1c40dede21))

# [1.3.0-alpha.8](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.7...v1.3.0-alpha.8) (2026-05-11)


### Features

* add is_system and slug fields to system-seeded models ([#78](https://github.com/Novanglus96/LenoreFin/issues/78)) ([ca652a8](https://github.com/Novanglus96/LenoreFin/commit/ca652a8981b4e04c9bbb318071ff5d11b40454b4))

# [1.3.0-alpha.7](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.6...v1.3.0-alpha.7) (2026-05-08)


### Bug Fixes

* reminder conversion now updates start_date to next non-excluded date ([#76](https://github.com/Novanglus96/LenoreFin/issues/76)) ([7d6b4ab](https://github.com/Novanglus96/LenoreFin/commit/7d6b4ab1ba1bc2906378041c8c186a3e9dfedb08))

# [1.3.0-alpha.6](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.5...v1.3.0-alpha.6) (2026-05-08)


### Bug Fixes

* restore csrf=False on auth classes broken by django-ninja 1.6 upgrade ([#77](https://github.com/Novanglus96/LenoreFin/issues/77)) ([c8f5edd](https://github.com/Novanglus96/LenoreFin/commit/c8f5eddfac98912661ddb4e2c6c54d38deb12367))

# [1.3.0-alpha.5](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.4...v1.3.0-alpha.5) (2026-05-08)


### Bug Fixes

* correct GITHUB_ENV writes in Compute project identifiers step ([#75](https://github.com/Novanglus96/LenoreFin/issues/75)) ([3000669](https://github.com/Novanglus96/LenoreFin/commit/3000669291114b5d5da816863bb4faf20723f4b1))

# [1.3.0-alpha.4](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.3...v1.3.0-alpha.4) (2026-05-08)


### Bug Fixes

* disabling an account no longer wipes open_date ([#74](https://github.com/Novanglus96/LenoreFin/issues/74)) ([4dec53a](https://github.com/Novanglus96/LenoreFin/commit/4dec53af855c81f82fa762abb35e11d132b79338))

# [1.3.0-alpha.3](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.2...v1.3.0-alpha.3) (2026-05-08)


### Bug Fixes

* correct budget percentage calculation when rollover produces negative starting balance ([#67](https://github.com/Novanglus96/LenoreFin/issues/67)) ([e4ffc23](https://github.com/Novanglus96/LenoreFin/commit/e4ffc23c83594ee7496fa3f7bbbd4082da7fd930))
* correct budget percentage calculation when rollover produces negative starting balance ([#68](https://github.com/Novanglus96/LenoreFin/issues/68)) ([29e942a](https://github.com/Novanglus96/LenoreFin/commit/29e942a268fd474bbc6dbad20f6e1cf2919a0550))

# [1.3.0-alpha.2](https://github.com/Novanglus96/LenoreFin/compare/v1.3.0-alpha.1...v1.3.0-alpha.2) (2026-05-08)


### Bug Fixes

* auth post-login bugs — superuser group, logout, 401 race ([#66](https://github.com/Novanglus96/LenoreFin/issues/66)) ([b2db4a0](https://github.com/Novanglus96/LenoreFin/commit/b2db4a0b2e8cd8be699b1e4d43a8826e42dfaf1d))

# [1.3.0-alpha.1](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0...v1.3.0-alpha.1) (2026-05-08)


### Features

* add session-based auth with group permissions (Full Access / Readonly) ([#65](https://github.com/Novanglus96/LenoreFin/issues/65)) ([85c6e07](https://github.com/Novanglus96/LenoreFin/commit/85c6e07db5a6138f5673b765f2bb2156f9195662))

# [1.2.0](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2...v1.2.0) (2026-05-07)


### Bug Fixes

* account available balance now includes pending ([39b5254](https://github.com/Novanglus96/LenoreFin/commit/39b5254f548d9ef190c742430140890325c9ad35))
* add Http404 handlers to payee view and restore import ([419ea82](https://github.com/Novanglus96/LenoreFin/commit/419ea82bfec6511f542834ff52b023249231fe11))
* add missing return statement in domain_repeat_to_schema mapper ([0f96826](https://github.com/Novanglus96/LenoreFin/commit/0f96826b2a9cc39da140729b1d626530ce24771f))
* budgets include pending transactions ([2bec572](https://github.com/Novanglus96/LenoreFin/commit/2bec57281206e75b721809984d9e8ba5f4bb2873))
* bust account balance caches on transaction create, clear, and delete ([386f920](https://github.com/Novanglus96/LenoreFin/commit/386f920d24884930bed00d225e762104956021ac))
* bust account caches after batch date edit ([d3d8a31](https://github.com/Novanglus96/LenoreFin/commit/d3d8a31c97a7ab2ee28e77b0b58e1ecfe9f7d844))
* bust old account caches when a transaction's account changes on edit ([6a85bcc](https://github.com/Novanglus96/LenoreFin/commit/6a85bccab612a1b120ec0ef55094b658e3d9da48))
* caclulator transfers/transactions wrong dates ([7b58ae0](https://github.com/Novanglus96/LenoreFin/commit/7b58ae0b3a99484929fb6b18712cdb912c026d1f))
* capture 404 error with ninja ([7e56aca](https://github.com/Novanglus96/LenoreFin/commit/7e56aca17bac072fe94bf65e013481af51d20603))
* clearing transactions now reloads cache ([8296657](https://github.com/Novanglus96/LenoreFin/commit/8296657232c776fc63051c94824f82884fc01441))
* clearing transactions now reloads cache ([#57](https://github.com/Novanglus96/LenoreFin/issues/57)) ([2712402](https://github.com/Novanglus96/LenoreFin/commit/271240228fd5cea770cee2f0a09b3025257d0406))
* correct forecast fill color and transaction cache invalidation ([5b2e5de](https://github.com/Novanglus96/LenoreFin/commit/5b2e5de290eed4c0e7a719a02959975b7addc214))
* edit account form, typo on pay_day ([26b6455](https://github.com/Novanglus96/LenoreFin/commit/26b64559a3a71fa87f40e193bec694f2b9b5cf5f))
* explicitly bust all account caches on single transaction edit ([fcdf587](https://github.com/Novanglus96/LenoreFin/commit/fcdf587bc33e3bceaa3371f6d7ddec8fa2b59b5a))
* failed backups ([e6aedb6](https://github.com/Novanglus96/LenoreFin/commit/e6aedb6fa5c9cdd6984616de2bad156877531690))
* forecasted reminder transfers had reverse pretty_total logic ([#50](https://github.com/Novanglus96/LenoreFin/issues/50)) ([82793c2](https://github.com/Novanglus96/LenoreFin/commit/82793c2038507065e1a51e9ab271990ce0534dad))
* incorrect escaping of backslash in tag __str__ ([f1e68ca](https://github.com/Novanglus96/LenoreFin/commit/f1e68ca16fa258de0ce8ef615f26793ea99baa1c))
* logs missing from production ([492cd33](https://github.com/Novanglus96/LenoreFin/commit/492cd3337ec59975ef4483cf1a66b1caa726c0ee))
* loop on forecast calc for cc ([5041529](https://github.com/Novanglus96/LenoreFin/commit/50415299d2ed071716b2ad9795fa852c8942e559))
* messages objects message_date now timezone aware ([839f470](https://github.com/Novanglus96/LenoreFin/commit/839f47009682cca9566ca77613988d4d5efc0c59))
* missing source account on new transactions ([f0a1931](https://github.com/Novanglus96/LenoreFin/commit/f0a1931b7238699507a33126c522518aea5f9034))
* pie graph failed when initializing ([df6053b](https://github.com/Novanglus96/LenoreFin/commit/df6053bee5e5427e8913679dc8639e0eff5ef889))
* pie graph percentages wrong ([#53](https://github.com/Novanglus96/LenoreFin/issues/53)) ([b5fb46e](https://github.com/Novanglus96/LenoreFin/commit/b5fb46e128ad346c8748900e1143f9199e042e59))
* query issues in prod with move to pydantic 2 ([#49](https://github.com/Novanglus96/LenoreFin/issues/49)) ([bccf97a](https://github.com/Novanglus96/LenoreFin/commit/bccf97a46914e576613af8eeec5b424935133c5d))
* reminder and forecast transactions source/dest account set null on delete ([f210ea4](https://github.com/Novanglus96/LenoreFin/commit/f210ea4d864eda9f143e93f134734562bb2db622))
* reminder dates now timezone correct in tables ([#61](https://github.com/Novanglus96/LenoreFin/issues/61)) ([57a66ae](https://github.com/Novanglus96/LenoreFin/commit/57a66ae77bad14dd6cee693f3d6b11ce45e54851))
* remove duplicate file deletion ([57d25ed](https://github.com/Novanglus96/LenoreFin/commit/57d25ed3cff1a756445354898a708988461494f0))
* restore forecast chart colors and remove invalid tag data guard ([0888798](https://github.com/Novanglus96/LenoreFin/commit/08887989f8e9b397b6b9b8e33da71ed3af6353ce)), closes [#06966](https://github.com/Novanglus96/LenoreFin/issues/06966)
* revert refetchQueries back to invalidateQueries for accounts on clear ([601d9a1](https://github.com/Novanglus96/LenoreFin/commit/601d9a1476c56d2afb492cb4795d82cef97e1283))
* show success snackbar after transaction update ([58225c5](https://github.com/Novanglus96/LenoreFin/commit/58225c5ec1104f18028c71b4716bb1788421af2c))
* signal wasn't ignoring irrelavent fields ([683fa42](https://github.com/Novanglus96/LenoreFin/commit/683fa42224538bfe263253c43c6497372247aa09))
* source account is required, no defaults ([b18bd6b](https://github.com/Novanglus96/LenoreFin/commit/b18bd6b15e90d768c6600d83c2a42a11be121bfe))
* synchronously refresh ReminderCacheTransaction on reminder-to-transaction conversion ([5ad6af7](https://github.com/Novanglus96/LenoreFin/commit/5ad6af7a4508ed5610d00649a7db4da69aa4ce75))
* tag child can be null, but not parent by default ([6487858](https://github.com/Novanglus96/LenoreFin/commit/6487858a0573a4ec1a8fbc31380ae8f83a7de073))
* transaction accounts set to null on account deletions at model level ([4c2dc46](https://github.com/Novanglus96/LenoreFin/commit/4c2dc46b5aaeecfc41838246ac2097e5c646b0e1))
* use account_all pattern for cache busting and force refetch on clear ([9802830](https://github.com/Novanglus96/LenoreFin/commit/9802830136fcf52f3d449ee490911aae17c17f63))
* use correct delete_pattern and centralize frontend cache invalidation ([eecee07](https://github.com/Novanglus96/LenoreFin/commit/eecee0787cad3c5ffe4f1663a3e850f03d3402da))
* use signal to ensure transaction images are deleted ([d6a8533](https://github.com/Novanglus96/LenoreFin/commit/d6a8533b8322068b76f97f644cb9867543352585))
* wire up transactions and accounts signals in AppConfig.ready() ([a58272a](https://github.com/Novanglus96/LenoreFin/commit/a58272afb5327ab96c54ea978591dbaf1f24197b))


### Features

* added a loading screen for frontend when backend is loading ([03e640a](https://github.com/Novanglus96/LenoreFin/commit/03e640a1c0eb14abb8cbf223cea7f631eccd143f))
* added reqrds graph ([c8a5a1b](https://github.com/Novanglus96/LenoreFin/commit/c8a5a1bb2d76ed6bf99871768ef4e2fe8a8fca68))
* caching tables ([#51](https://github.com/Novanglus96/LenoreFin/issues/51)) ([cc9c651](https://github.com/Novanglus96/LenoreFin/commit/cc9c651b2fcdf5a53178068ccbbd6d406452fea0))
* calculate credit card bill ([#43](https://github.com/Novanglus96/LenoreFin/issues/43)) ([01cf855](https://github.com/Novanglus96/LenoreFin/commit/01cf85518ca569c38e1073fd280fde5494479e06))
* extract service layer and add comprehensive test coverage ([7a5f006](https://github.com/Novanglus96/LenoreFin/commit/7a5f00632bd6862fb82a1584e89dc0d5ab701c53))
* extract service layer and add comprehensive test coverage across all apps ([f6bcb0a](https://github.com/Novanglus96/LenoreFin/commit/f6bcb0aa8b4c9ce4ef5b34df0cbb3d256bf972a9))
* improve mobile design ([#48](https://github.com/Novanglus96/LenoreFin/issues/48)) ([27a1b5e](https://github.com/Novanglus96/LenoreFin/commit/27a1b5e6510aaf990f4a83afff5ea3585dfb547a))
* logging ([#52](https://github.com/Novanglus96/LenoreFin/issues/52)) ([2544d61](https://github.com/Novanglus96/LenoreFin/commit/2544d61a741cb02d979146f8222be2ed04eadb88))

# [1.2.0-rc.14](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.13...v1.2.0-rc.14) (2025-12-23)


### Bug Fixes

* reminder dates now timezone correct in tables ([#61](https://github.com/Novanglus96/LenoreFin/issues/61)) ([57a66ae](https://github.com/Novanglus96/LenoreFin/commit/57a66ae77bad14dd6cee693f3d6b11ce45e54851))

# [1.2.0-rc.13](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.12...v1.2.0-rc.13) (2025-12-11)


### Bug Fixes

* edit account form, typo on pay_day ([26b6455](https://github.com/Novanglus96/LenoreFin/commit/26b64559a3a71fa87f40e193bec694f2b9b5cf5f))
* loop on forecast calc for cc ([5041529](https://github.com/Novanglus96/LenoreFin/commit/50415299d2ed071716b2ad9795fa852c8942e559))

# [1.2.0-rc.12](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.11...v1.2.0-rc.12) (2025-12-11)


### Bug Fixes

* caclulator transfers/transactions wrong dates ([7b58ae0](https://github.com/Novanglus96/LenoreFin/commit/7b58ae0b3a99484929fb6b18712cdb912c026d1f))
* clearing transactions now reloads cache ([8296657](https://github.com/Novanglus96/LenoreFin/commit/8296657232c776fc63051c94824f82884fc01441))
* failed backups ([e6aedb6](https://github.com/Novanglus96/LenoreFin/commit/e6aedb6fa5c9cdd6984616de2bad156877531690))
* missing source account on new transactions ([f0a1931](https://github.com/Novanglus96/LenoreFin/commit/f0a1931b7238699507a33126c522518aea5f9034))

# [1.2.0-rc.11](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.10...v1.2.0-rc.11) (2025-12-11)


### Features

* added reqrds graph ([c8a5a1b](https://github.com/Novanglus96/LenoreFin/commit/c8a5a1bb2d76ed6bf99871768ef4e2fe8a8fca68))

# [1.2.0-rc.10](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.9...v1.2.0-rc.10) (2025-12-10)


### Bug Fixes

* clearing transactions now reloads cache ([#57](https://github.com/Novanglus96/LenoreFin/issues/57)) ([2712402](https://github.com/Novanglus96/LenoreFin/commit/271240228fd5cea770cee2f0a09b3025257d0406))

# [1.2.0-rc.9](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.8...v1.2.0-rc.9) (2025-12-09)


### Bug Fixes

* account available balance now includes pending ([39b5254](https://github.com/Novanglus96/LenoreFin/commit/39b5254f548d9ef190c742430140890325c9ad35))
* budgets include pending transactions ([2bec572](https://github.com/Novanglus96/LenoreFin/commit/2bec57281206e75b721809984d9e8ba5f4bb2873))

# [1.2.0-rc.8](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.7...v1.2.0-rc.8) (2025-12-08)


### Bug Fixes

* logs missing from production ([492cd33](https://github.com/Novanglus96/LenoreFin/commit/492cd3337ec59975ef4483cf1a66b1caa726c0ee))
* pie graph failed when initializing ([df6053b](https://github.com/Novanglus96/LenoreFin/commit/df6053bee5e5427e8913679dc8639e0eff5ef889))

# [1.2.0-rc.7](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.6...v1.2.0-rc.7) (2025-12-08)


### Bug Fixes

* pie graph percentages wrong ([#53](https://github.com/Novanglus96/LenoreFin/issues/53)) ([b5fb46e](https://github.com/Novanglus96/LenoreFin/commit/b5fb46e128ad346c8748900e1143f9199e042e59))

# [1.2.0-rc.6](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.5...v1.2.0-rc.6) (2025-12-05)


### Features

* logging ([#52](https://github.com/Novanglus96/LenoreFin/issues/52)) ([2544d61](https://github.com/Novanglus96/LenoreFin/commit/2544d61a741cb02d979146f8222be2ed04eadb88))

# [1.2.0-rc.5](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.4...v1.2.0-rc.5) (2025-12-04)


### Features

* caching tables ([#51](https://github.com/Novanglus96/LenoreFin/issues/51)) ([cc9c651](https://github.com/Novanglus96/LenoreFin/commit/cc9c651b2fcdf5a53178068ccbbd6d406452fea0))

# [1.2.0-rc.4](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.3...v1.2.0-rc.4) (2025-10-24)


### Bug Fixes

* forecasted reminder transfers had reverse pretty_total logic ([#50](https://github.com/Novanglus96/LenoreFin/issues/50)) ([82793c2](https://github.com/Novanglus96/LenoreFin/commit/82793c2038507065e1a51e9ab271990ce0534dad))

# [1.2.0-rc.3](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.2...v1.2.0-rc.3) (2025-10-23)


### Bug Fixes

* query issues in prod with move to pydantic 2 ([#49](https://github.com/Novanglus96/LenoreFin/issues/49)) ([bccf97a](https://github.com/Novanglus96/LenoreFin/commit/bccf97a46914e576613af8eeec5b424935133c5d))

# [1.2.0-rc.2](https://github.com/Novanglus96/LenoreFin/compare/v1.2.0-rc.1...v1.2.0-rc.2) (2025-10-23)


### Features

* improve mobile design ([#48](https://github.com/Novanglus96/LenoreFin/issues/48)) ([27a1b5e](https://github.com/Novanglus96/LenoreFin/commit/27a1b5e6510aaf990f4a83afff5ea3585dfb547a))

# [1.2.0-rc.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2...v1.2.0-rc.1) (2025-08-25)


### Features

* added a loading screen for frontend when backend is loading ([03e640a](https://github.com/Novanglus96/LenoreFin/commit/03e640a1c0eb14abb8cbf223cea7f631eccd143f))
* calculate credit card bill ([#43](https://github.com/Novanglus96/LenoreFin/issues/43)) ([01cf855](https://github.com/Novanglus96/LenoreFin/commit/01cf85518ca569c38e1073fd280fde5494479e06))

# [1.2.0-rc.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2...v1.2.0-rc.1) (2025-07-22)


### Features

* added a loading screen for frontend when backend is loading ([03e640a](https://github.com/Novanglus96/LenoreFin/commit/03e640a1c0eb14abb8cbf223cea7f631eccd143f))

# [1.2.0-rc.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2...v1.2.0-rc.1) (2025-07-22)


### Features

* added a loading screen for frontend when backend is loading ([03e640a](https://github.com/Novanglus96/LenoreFin/commit/03e640a1c0eb14abb8cbf223cea7f631eccd143f))

# [1.2.0-rc.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2...v1.2.0-rc.1) (2025-07-22)


### Features

* added a loading screen for frontend when backend is loading ([03e640a](https://github.com/Novanglus96/LenoreFin/commit/03e640a1c0eb14abb8cbf223cea7f631eccd143f))

## [1.1.2](https://github.com/Novanglus96/LenoreFin/compare/v1.1.1...v1.1.2) (2025-07-21)


### Bug Fixes

* remove another duplicate entry from changelog ([1c2238c](https://github.com/Novanglus96/LenoreFin/commit/1c2238cb703d1da26c0d13c47ab4913593cc8644))
* remove duplicate changelog entries ([41ee633](https://github.com/Novanglus96/LenoreFin/commit/41ee633e281e865b6f374bb4fe534146b9d3291f))
* update version to accept alpha, beta, rc prereleases ([09d81d6](https://github.com/Novanglus96/LenoreFin/commit/09d81d65e272a58fad40e5a601236674ea2cef8c))

## [1.1.2-rc.2](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2-rc.1...v1.1.2-rc.2) (2025-07-21)


### Bug Fixes

* update version to accept alpha, beta, rc prereleases ([09d81d6](https://github.com/Novanglus96/LenoreFin/commit/09d81d65e272a58fad40e5a601236674ea2cef8c))

## [1.1.2-rc.2](https://github.com/Novanglus96/LenoreFin/compare/v1.1.2-rc.1...v1.1.2-rc.2) (2025-07-21)


### Bug Fixes

* update version to accept alpha, beta, rc prereleases ([09d81d6](https://github.com/Novanglus96/LenoreFin/commit/09d81d65e272a58fad40e5a601236674ea2cef8c))

## [1.1.2-rc.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.1...v1.1.2-rc.1) (2025-07-18)


### Bug Fixes

* remove another duplicate entry from changelog ([1c2238c](https://github.com/Novanglus96/LenoreFin/commit/1c2238cb703d1da26c0d13c47ab4913593cc8644))
* remove duplicate changelog entries ([41ee633](https://github.com/Novanglus96/LenoreFin/commit/41ee633e281e865b6f374bb4fe534146b9d3291f))

## [1.1.2-rc.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.1...v1.1.2-rc.1) (2025-07-18)


### Bug Fixes

* remove another duplicate entry from changelog ([1c2238c](https://github.com/Novanglus96/LenoreFin/commit/1c2238cb703d1da26c0d13c47ab4913593cc8644))
* remove duplicate changelog entries ([41ee633](https://github.com/Novanglus96/LenoreFin/commit/41ee633e281e865b6f374bb4fe534146b9d3291f))

## [1.1.1](https://github.com/Novanglus96/LenoreFin/compare/v1.1.0...v1.1.1) (2025-07-17)


### Bug Fixes

* backend version pulls dynamically from VERSION file ([#20](https://github.com/Novanglus96/LenoreFin/issues/20)) ([e33c57b](https://github.com/Novanglus96/LenoreFin/commit/e33c57bb4584ee91e8d064d6c3813b93915618e4))
* frontend version loads from package.json ([#22](https://github.com/Novanglus96/LenoreFin/issues/22)) ([5c755da](https://github.com/Novanglus96/LenoreFin/commit/5c755da3db90261f1b3449ed579724197a4e7836))
* please release version file changed to VERSION file ([#21](https://github.com/Novanglus96/LenoreFin/issues/21)) ([3e0bcec](https://github.com/Novanglus96/LenoreFin/commit/3e0bcec59f8d0d93f58c7522de44b1730939d18d))

# Changelog

## [1.2.1](https://github.com/Novanglus96/LenoreFin/compare/LenoreFin-v1.2.0...LenoreFin-v1.2.1) (2025-07-17)


### Bug Fixes

* backend version pulls dynamically from VERSION file ([#20](https://github.com/Novanglus96/LenoreFin/issues/20)) ([e33c57b](https://github.com/Novanglus96/LenoreFin/commit/e33c57bb4584ee91e8d064d6c3813b93915618e4))
* frontend version loads from package.json ([#22](https://github.com/Novanglus96/LenoreFin/issues/22)) ([5c755da](https://github.com/Novanglus96/LenoreFin/commit/5c755da3db90261f1b3449ed579724197a4e7836))
* please release version file changed to VERSION file ([#21](https://github.com/Novanglus96/LenoreFin/issues/21)) ([3e0bcec](https://github.com/Novanglus96/LenoreFin/commit/3e0bcec59f8d0d93f58c7522de44b1730939d18d))

## [1.2.0](https://github.com/Novanglus96/LenoreFin/compare/LenoreFin-v1.1.0...LenoreFin-v1.2.0) (2025-07-16)


### Features

* converted from vue-cli to vite ([#4](https://github.com/Novanglus96/LenoreFin/issues/4)) ([014133b](https://github.com/Novanglus96/LenoreFin/commit/014133bf0e482e0c21a9d02695c86a956646621b))
* single env file setup ([#6](https://github.com/Novanglus96/LenoreFin/issues/6)) ([39facf0](https://github.com/Novanglus96/LenoreFin/commit/39facf07127117752988d37cd20b7df761665b80))


### Bug Fixes

* account balance calculation ([c7b5d49](https://github.com/Novanglus96/LenoreFin/commit/c7b5d497338f829dee8d41a218f0deaa85184edf))
* account creation error, remove rewards amount ([fe7fbcb](https://github.com/Novanglus96/LenoreFin/commit/fe7fbcb2a15cbfa60fc69c7bc969843710c797c8))
* account update now working ([2157453](https://github.com/Novanglus96/LenoreFin/commit/215745329f944f7c577681fac84e5f6086953db5))
* add icons in jazzmin for new tag tables ([f66a723](https://github.com/Novanglus96/LenoreFin/commit/f66a72375d6de3b1a9bd04574b99764aaa5f19df))
* add rounding to dataset in planning graph data ([7bc9c75](https://github.com/Novanglus96/LenoreFin/commit/7bc9c758f0b524a4a7c14dc85faa1db9c1efc064))
* add time to messages ([73629ea](https://github.com/Novanglus96/LenoreFin/commit/73629ea4f5c16e8a666a9a2eae6afc63babd3ffa))
* add, delete and clear buttons now consider reminder transactions ([5f79a79](https://github.com/Novanglus96/LenoreFin/commit/5f79a7936d960f5f477b8a70b227ec83e5da1d1e))
* adding tags ([ba43972](https://github.com/Novanglus96/LenoreFin/commit/ba43972a292cc1013148d8bf52606347dc0eb8ad))
* adding transactions corrected to new api endpoint url ([22f4886](https://github.com/Novanglus96/LenoreFin/commit/22f488602227b48326099d20426003a357b08ad4))
* adjust balance cast to flaot with 2 decimal points ([0d0a74f](https://github.com/Novanglus96/LenoreFin/commit/0d0a74fce013a511f5439358d9dc6a7cf5b1a51a))
* admin logo display on production ([b456ef0](https://github.com/Novanglus96/LenoreFin/commit/b456ef0607bcba80b43d4a37b1600d01790f9d50))
* api date operations use local timezone ([71d7364](https://github.com/Novanglus96/LenoreFin/commit/71d7364d6ecf6f00e3786e9de4089ad7f9f8ef7a))
* api_key runtime injection for production ([77ca15b](https://github.com/Novanglus96/LenoreFin/commit/77ca15b6e90926e34dc521184317975a8969ce93))
* auto add of reminders with new tag toggle fixed ([85124bd](https://github.com/Novanglus96/LenoreFin/commit/85124bde30c6753ad638f969d7b0c915e8aee719))
* auto add reminders doesn't update reminder dates ([428c0f0](https://github.com/Novanglus96/LenoreFin/commit/428c0f07880c86bc2d83c59a29618c555c9cf830))
* available credit calculation ([66b7f81](https://github.com/Novanglus96/LenoreFin/commit/66b7f81e2f5a4a3fbbe59f9968913ea934f72082))
* balance adjustment wrong for negative balances ([a24bb8c](https://github.com/Novanglus96/LenoreFin/commit/a24bb8ce7e0b37f17f7db2c29b65529c96891718))
* balance does not include opening balance currently ([311b444](https://github.com/Novanglus96/LenoreFin/commit/311b444a15582ce05ac26db33736c6b795a3d7d1))
* balance now includes opening_balance ([47d0fce](https://github.com/Novanglus96/LenoreFin/commit/47d0fce54102c0716d94d5bfcc1b5faebc7e2f1a))
* calcluator memo has 2 decimal places ([a05ee57](https://github.com/Novanglus96/LenoreFin/commit/a05ee577d12f11252a1f18922562a4e33490ad08))
* calculator decimal and precision issues ([fec3851](https://github.com/Novanglus96/LenoreFin/commit/fec3851f710c73a677949bef7355e0851f9b1afb))
* calculator missing transfer transactions ([36d1c0a](https://github.com/Novanglus96/LenoreFin/commit/36d1c0afedbef142184c0ea95cb2b863f5382c35))
* clear transaction ([2ae0180](https://github.com/Novanglus96/LenoreFin/commit/2ae0180fd0d2b3c03fc58029c11ddc56d58df784))
* clear transactions, add reminder transactions ([b0b190e](https://github.com/Novanglus96/LenoreFin/commit/b0b190e4d8733b963fc64c0f8eb29bf7c127398f))
* color change for selected budget ([4a1ea95](https://github.com/Novanglus96/LenoreFin/commit/4a1ea957e931384f3134e37ab52171845a6412f4))
* converting reminder to transaction ([0e2b354](https://github.com/Novanglus96/LenoreFin/commit/0e2b35460b460c7a1d08f77cc493146051ed81d3))
* converting reminders to transactions task ([37beed2](https://github.com/Novanglus96/LenoreFin/commit/37beed22ed280934b7764636b180b261d6911ce4))
* debug mode on dev only ([884009b](https://github.com/Novanglus96/LenoreFin/commit/884009bee3d90fbce3c2daa148d9c16b6036438f))
* default tab set for transaction form ([bd9d483](https://github.com/Novanglus96/LenoreFin/commit/bd9d483abd88f384466fdfc0faac393d725c32cd))
* defineOptions missing import ([5383b01](https://github.com/Novanglus96/LenoreFin/commit/5383b01c3aea01209ec2414bb1d45e63bd997d3b))
* deleting reminder ([8745f02](https://github.com/Novanglus96/LenoreFin/commit/8745f0257546bdfcc9b2399f68b289ee0b855003))
* deleting reminders is more effecient ([e5e847b](https://github.com/Novanglus96/LenoreFin/commit/e5e847b05e341b7a214278868ca61d2279171031))
* display memo in calculator multiline ([f8b6cad](https://github.com/Novanglus96/LenoreFin/commit/f8b6cad59ff90fed6919bbeefe963142b847c51d))
* docker file build error with netcat isntall source ([8c7d4d1](https://github.com/Novanglus96/LenoreFin/commit/8c7d4d152c19eee9fa872dd056992118b14c34cc))
* docker file changes ([adea4ca](https://github.com/Novanglus96/LenoreFin/commit/adea4ca33d6008588d4209f685b8c02135ff7b4c))
* don't display tag icon if no tag or upcoming transactions ([11d0190](https://github.com/Novanglus96/LenoreFin/commit/11d0190b2baf520828d23aea4fe7463383b05f77))
* duplicate key error ([4dbe0c6](https://github.com/Novanglus96/LenoreFin/commit/4dbe0c6de0fe3d3a43a61ba9c3b5641e3acd98fe))
* duplicate transactions in budget total, calcualtor list ([b7e5a9e](https://github.com/Novanglus96/LenoreFin/commit/b7e5a9e410a1ddfce8f9db993440a60409d57826))
* editing date triggers form check ([1010025](https://github.com/Novanglus96/LenoreFin/commit/10100256a3b1a335b227ad000c41064faa2ddb31))
* editing transactions with tags ([51afcf0](https://github.com/Novanglus96/LenoreFin/commit/51afcf025fabfe5da230f9dcb780dddbd33897dc))
* enable delete log entries ([dbde98f](https://github.com/Novanglus96/LenoreFin/commit/dbde98fd8315f6c3523661724d4cd72d34418759))
* expenses/income widgets sum parents ([e5d8e36](https://github.com/Novanglus96/LenoreFin/commit/e5d8e36d585f79d53e1669f273c503424602ef1f))
* file import tag creation ([6fb2b85](https://github.com/Novanglus96/LenoreFin/commit/6fb2b850f9c78b0df90e6d54bd03b0f0f757bc3f))
* fix money formatting in GUI ([d0d4155](https://github.com/Novanglus96/LenoreFin/commit/d0d415586b0bcb8a6a54fb880b2441da20a4a6d1))
* fixed deprecated active-color ([76e284f](https://github.com/Novanglus96/LenoreFin/commit/76e284f31acfa4af11ce8c1e3881b7e4c45a00ca))
* fixture for options typo on exclude ([053e9e8](https://github.com/Novanglus96/LenoreFin/commit/053e9e86cd99f48298a1c05c5739c4a72b6d1027))
* forecast graph now returns correct balances ([c9f76ee](https://github.com/Novanglus96/LenoreFin/commit/c9f76ee9ad4def1a9fb9e35e1ff41482f6af2239))
* forecast transactions match timeframe ([a5221ff](https://github.com/Novanglus96/LenoreFin/commit/a5221ff36ad589a47e8fe43ee93bd6778248979b))
* forecast transactions now set to correct view type and resets as appropiate ([dcf03fc](https://github.com/Novanglus96/LenoreFin/commit/dcf03fc2961d234e6584b5a9e5929ec2cad33f07))
* form validation reset on close ([ca80168](https://github.com/Novanglus96/LenoreFin/commit/ca801687da0095f70fd7ee49d6cfc40c02a51e4e))
* graph issues for tags, year not specified and status should not be pending ([87ddfa0](https://github.com/Novanglus96/LenoreFin/commit/87ddfa0267a7abc8003520f558c26615fbb2f31a))
* graphs prvious data now calculates properly when no data in range ([5cb7d6c](https://github.com/Novanglus96/LenoreFin/commit/5cb7d6cad6ac63b0d8f0139ab60cca2a6ce30a18))
* gui change to contributions ([7386c90](https://github.com/Novanglus96/LenoreFin/commit/7386c9071185c387e67e645ec788fa1aeb49ac42))
* health calculator passing data ([7e3b0a9](https://github.com/Novanglus96/LenoreFin/commit/7e3b0a9ecdef48334737cf620940e9a948ccfb7f))
* import of transactions creates details correctly for transfers ([042d1e5](https://github.com/Novanglus96/LenoreFin/commit/042d1e58bda81dde5b0f308c05b49921cae39537))
* increase upload size to 100mb ([495021d](https://github.com/Novanglus96/LenoreFin/commit/495021d89072d4a3ffd4f3522238f6510c913c36))
* logic error in reminder forecast transactions ([56fc56a](https://github.com/Novanglus96/LenoreFin/commit/56fc56a113723180eb12fd67aa40828e5dc021e7))
* logo display in admin ([370cc9a](https://github.com/Novanglus96/LenoreFin/commit/370cc9a26b56552d7079eb14c1348f02ca742d25))
* migration issues with dates in models ([305fa11](https://github.com/Novanglus96/LenoreFin/commit/305fa117c48009832f0e96fd8ceaa0bbcff2d953))
* minor tweaks to widget graphs display ([e9f19bc](https://github.com/Novanglus96/LenoreFin/commit/e9f19bc23b8842063f55487f769a62124e5b9e02))
* missing api_key env variable ([8fee905](https://github.com/Novanglus96/LenoreFin/commit/8fee905a5199674109d8e21acdb1601046a9af29))
* missing imports from account model ([f6fdd0d](https://github.com/Novanglus96/LenoreFin/commit/f6fdd0d18bcfdf5fdd88595313d870f2891bdc0f))
* missing pretty account name on non transfers ([40272a5](https://github.com/Novanglus96/LenoreFin/commit/40272a5eab2514fae69df219421508d48625d944))
* next date updated when adding reminder transactions ([363e786](https://github.com/Novanglus96/LenoreFin/commit/363e78677e4f025004c080703ff0e0ae85417822))
* note str method on model conerted to string ([fc8c317](https://github.com/Novanglus96/LenoreFin/commit/fc8c317c740bb8b09941a40930ceefa807be94cf))
* null default values ([b73f451](https://github.com/Novanglus96/LenoreFin/commit/b73f451ce5deba5436f773ac1e39a73e58d03d8c))
* options don't overwrite ([4ad5ef2](https://github.com/Novanglus96/LenoreFin/commit/4ad5ef2572bb0e3d7391bf4e60f6138b6d76cb0c))
* pay graph typo for last year dec total (hard set to gross) ([4166346](https://github.com/Novanglus96/LenoreFin/commit/416634679d617f8e9a0353c541a4a906f48b7dbb))
* paycheck health calculator ([34290f7](https://github.com/Novanglus96/LenoreFin/commit/34290f76b5a981af0ba2896b0209298d728dbeea))
* paycheck validation error ([878f008](https://github.com/Novanglus96/LenoreFin/commit/878f008ad34337ea52488ba672ffb9961a233e04))
* precision error in calculator ([56f1514](https://github.com/Novanglus96/LenoreFin/commit/56f15145623dbf25e28b419e3c7d90f99deb1f02))
* prop types on account widgets change to array ([8dfde4f](https://github.com/Novanglus96/LenoreFin/commit/8dfde4f65c2019be991d74aa4c447219ad8b767a))
* reminder with no end_date now updates correctly when editing a trans ([eb85033](https://github.com/Novanglus96/LenoreFin/commit/eb85033d12c135d5b05915d5906bc5fd143d26f8))
* reminders with no end date broke forecast ([29fdfb4](https://github.com/Novanglus96/LenoreFin/commit/29fdfb4bc9fe3f7862bb90926f2dc3e7f089a0c8))
* remove unsed show model ([f483e56](https://github.com/Novanglus96/LenoreFin/commit/f483e566873ff12dfb50f6a4c02f513c41009180))
* remove unused emits ([aedc058](https://github.com/Novanglus96/LenoreFin/commit/aedc058f5e17916fdaa16b00db47617476a4078a))
* removed debug console logs ([3060004](https://github.com/Novanglus96/LenoreFin/commit/30600048f460ef74b827d7524ca113b795152a8f))
* removed hardcoded API key.  Now pulls from .env ([#5](https://github.com/Novanglus96/LenoreFin/issues/5)) ([adccad8](https://github.com/Novanglus96/LenoreFin/commit/adccad814bfdeb25acffb055c239331b370cc554))
* report for sub reports ([858333b](https://github.com/Novanglus96/LenoreFin/commit/858333bf1dfcaf47debbcf2ecf63b83f68e64313))
* rouding issue on averages ([5c1bcd7](https://github.com/Novanglus96/LenoreFin/commit/5c1bcd744ad7fb857de4d1dfbc3ef3a33d4ad6b1))
* size adjustment to reminder/upcoming transaction widgets ([552b2b5](https://github.com/Novanglus96/LenoreFin/commit/552b2b5b7bd694fd69af6e6549df3dbd4fedc3a9))
* slash in tag name ([31be490](https://github.com/Novanglus96/LenoreFin/commit/31be490eb263fdfbd35cc53fcb5d9a383f5c583f))
* small screen accounts menu color display ([f300c04](https://github.com/Novanglus96/LenoreFin/commit/f300c0425777a0bcd318e546b1213789948c0e89))
* sort order for exclusions in admin ([1a9666d](https://github.com/Novanglus96/LenoreFin/commit/1a9666d2c2ae034c3805d038bd695f8dd3a67c36))
* sort order of description history ([f7e73f3](https://github.com/Novanglus96/LenoreFin/commit/f7e73f3bd9d152f020e8a634b165e3ce2fd37d41))
* sort order of transactions ([61c09c9](https://github.com/Novanglus96/LenoreFin/commit/61c09c9475d18dd97e9f5e1daf419aa442d9d0de))
* sorting issue on tables in production ([b29daab](https://github.com/Novanglus96/LenoreFin/commit/b29daab14f46ea0db7807704b69a200e875c3f9f))
* sorting issues ([7c6fa3e](https://github.com/Novanglus96/LenoreFin/commit/7c6fa3e07af9372ad9c23f575fd8cb24006b6519))
* split amounts in calculator ([1da6e7f](https://github.com/Novanglus96/LenoreFin/commit/1da6e7fe94be6d2010c9b264f5d0a4dbfcc77e8d))
* sticky first column in reports ([deaa809](https://github.com/Novanglus96/LenoreFin/commit/deaa8097f8a3d99d63ea7a8ae6fda25e9859f143))
* tab dispaly correctly on transaction form ([f794b60](https://github.com/Novanglus96/LenoreFin/commit/f794b60589540351a2f381348fa20cd088054d17))
* table sizing issue with transacation tables ([a78f6d7](https://github.com/Novanglus96/LenoreFin/commit/a78f6d73f398722ff77f1ea119af741d37945f07))
* table sizing issues with sticky_headers ([d888f5d](https://github.com/Novanglus96/LenoreFin/commit/d888f5d6a415ba7703238166f4c7687a0469575a))
* tag addition ([088918d](https://github.com/Novanglus96/LenoreFin/commit/088918d987432ace1f9c9adf3a7d65ce1142311f))
* tag data verified before adding ([7c26824](https://github.com/Novanglus96/LenoreFin/commit/7c26824a34146f57bae38e15385195d0551c53bb))
* tag display and ordering ([55c2520](https://github.com/Novanglus96/LenoreFin/commit/55c2520f9668e030556ed9afec5a25bd38b5f235))
* tag name in tag table dispaly ([17915d2](https://github.com/Novanglus96/LenoreFin/commit/17915d2c82e7ddc877e83d20fefec27382467841))
* tag table sizing issue with sticky header ([0d886ee](https://github.com/Novanglus96/LenoreFin/commit/0d886eed5352a75563e4f0b42621de8bc279f918))
* tag transactions and graph ([13a390f](https://github.com/Novanglus96/LenoreFin/commit/13a390f59fa0e82a2a053725892f21e0c39664c9))
* tag validation with full_toggle ([831d5e6](https://github.com/Novanglus96/LenoreFin/commit/831d5e6d50217ba3ed0d262a446cb163a83cfb99))
* tagAmount validation error ([7bd8fbf](https://github.com/Novanglus96/LenoreFin/commit/7bd8fbf2afb0c2ddf4f2ad2972cf54ab71684fd6))
* tags not checked if transfer ([97f758c](https://github.com/Novanglus96/LenoreFin/commit/97f758cc78467d3ed77f9a9d16ffc77f897b56fa))
* timezone issue in prod ([cc1e4f4](https://github.com/Novanglus96/LenoreFin/commit/cc1e4f4c9928692b08ccc2b4fd4df80623103d78))
* timezone issue with scheduled tasks ([d7a62d4](https://github.com/Novanglus96/LenoreFin/commit/d7a62d4537a3afaf7e6810b7dcc2abb9d5970276))
* timezone on tasks ([be35c36](https://github.com/Novanglus96/LenoreFin/commit/be35c3687f6a4318c39a229c16dd714295533ba2))
* transaction and account balance decimal places now 2 ([c06bf00](https://github.com/Novanglus96/LenoreFin/commit/c06bf007406c8fa41386bcb4c035c4a07a83f66d))
* transaction form paycheck value validation ([79b0e7f](https://github.com/Novanglus96/LenoreFin/commit/79b0e7fddd182d37c12c152f603d39f21419624f))
* transaction list, forecast transaction list ([5dc8baa](https://github.com/Novanglus96/LenoreFin/commit/5dc8baac26e424da164ef7dbdc0c3d58cf747cfa))
* transaction total triggers tag check ([3535d06](https://github.com/Novanglus96/LenoreFin/commit/3535d064a750c96e302cc6058021d415a6e948fd))
* transactions load temp from reminders ([ea6a89e](https://github.com/Novanglus96/LenoreFin/commit/ea6a89ee409ff6a17fff38bb9ba9c1644e31ab46))
* transactions now show for forecasts ([bf62982](https://github.com/Novanglus96/LenoreFin/commit/bf6298210ebd0f4ece77830f43fac82566567bcb))
* transfer tag issue ([bb8ccaa](https://github.com/Novanglus96/LenoreFin/commit/bb8ccaa0d773579367bd86cb0bdd54e60a3f1d8f))
* typo in balance calc effecting reminders ([80b21d3](https://github.com/Novanglus96/LenoreFin/commit/80b21d3e545efbcbc130c1ca9a16f5310d2ea4d7))
* typo in version number ([5c5c7fa](https://github.com/Novanglus96/LenoreFin/commit/5c5c7fa7a2cd6d81a26c2c5e58046c28e4aa376f))
* unique temp ids for reminder transactions ([5afde0b](https://github.com/Novanglus96/LenoreFin/commit/5afde0b964553b8aac1badd9ec5725cdba144321))
* untagged widgets ([09b47b8](https://github.com/Novanglus96/LenoreFin/commit/09b47b831d950595eee74ece24d3cf03d79075a6))
* unused handleReset ([cafd961](https://github.com/Novanglus96/LenoreFin/commit/cafd961c39c4f1970d6d37675add8ea7027110cc))
* unused select on table ([c89a993](https://github.com/Novanglus96/LenoreFin/commit/c89a993dad1b7b023836bbce808039dfc176b23d))
* unused variable ([57fa193](https://github.com/Novanglus96/LenoreFin/commit/57fa1938e65700be1f9cf8ced4b7d80b19bfa42c))
* unused variables in api ([312ce75](https://github.com/Novanglus96/LenoreFin/commit/312ce75da2fa5035d0c23d71a9b35a2ce1904252))
* upcoming transactions cleaned up and using subqueries ([de61d0a](https://github.com/Novanglus96/LenoreFin/commit/de61d0a7e03060fdd75c8e6d5181cb1bd862484c))
* upcoming transactions with multiple tags ([e852160](https://github.com/Novanglus96/LenoreFin/commit/e8521600fa35b07dcff4761bc3f89f0ba6b30fb7))
* updates to memo field trigger form check ([8e4d475](https://github.com/Novanglus96/LenoreFin/commit/8e4d4757f5230fed6d72ed37621f824c2643daab))
* use store for selection of transactions ([3a15f6c](https://github.com/Novanglus96/LenoreFin/commit/3a15f6ccb631a45390fd0721dae8bf3326d02d4e))
* vue hydration errors ([326a67a](https://github.com/Novanglus96/LenoreFin/commit/326a67a4050daa78a47ccb273f90fb6e89af9e7b))
* widget graphs ([7c3b33a](https://github.com/Novanglus96/LenoreFin/commit/7c3b33a18fef0b2c9ab925f42301c569c013ad36))
