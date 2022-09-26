<script setup lang="ts">
import { useDarkmode } from "/@src/stores/darkmode";

import Iconify from "@iconify/iconify";
import { computed, ref, watch } from "vue";

export type VCardMediaFormat = "4by3" | "16by9";
export interface VCardMediaProps {
  image?: string;
  video?: string;
  placeholder?: string;
  format?: VCardMediaFormat;
  videoFormat?:
    | "video/mp4"
    | "video/quicktime"
    | "video/x-flv"
    | "application/x-mpegURL"
    | "video/MP2T"
    | "video/3gpp"
    | "video/x-msvideo"
    | "video/x-ms-wmv";
}

const props = withDefaults(defineProps<VCardMediaProps>(), {
  format: "16by9",
  videoMimeType: "video/mp4",
});

const darkmode = useDarkmode();

const iconifyDataUrl = (
  icon: string,
  style: Partial<CSSStyleDeclaration> = {}
) => {
  const svgNoStream: SVGElement | null = Iconify.renderSVG(icon);
  let dataUrl =
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
  if (svgNoStream) {
    Object.keys(style).forEach((prop) => {
      // @ts-ignore
      svgNoStream.style[prop] = style[prop];
    });
    dataUrl = `data:image/svg+xml;base64,${btoa(svgNoStream.outerHTML)}`;
  }

  return dataUrl;
};

const backgroundGreyColor = () =>
  getComputedStyle(document.documentElement).getPropertyValue(
    "--background-grey"
  );

watch(
  () => darkmode.isDark,
  () => {
    svgStyles.value.color = backgroundGreyColor();
  }
);

const svgStyles = ref({
  color: backgroundGreyColor(),
  transform: "scale(0.6)",
});
const hasError = ref(false);
const playVideo = ref(false);

const _placeholder = computed(
  () => props.placeholder || iconifyDataUrl("carbon:no-image", svgStyles.value)
);
const _image = computed(
  () =>
    (hasError.value && _placeholder.value) ||
    props.image ||
    iconifyDataUrl("carbon:media-cast", svgStyles.value)
);
</script>
<template>
  <figure
    class="image is-16by9"
    :class="[props.format && `is-${props.format}`]"
  >
    <VButton
      class="toggle-button"
      v-if="image && video"
      icon="carbon:play-filled"
      color="primary"
      fullwidth
      @click="playVideo = !playVideo"
      >Toggle video/image</VButton
    >
    <img v-if="!playVideo" :src="_image" @error="hasError = true" />
    <video v-if="video && playVideo" controls>
      <source :src="video" :type="videoMimeType" />
    </video>
  </figure>
</template>

<style lang="postcss">
.image .toggle-button {
  position: absolute;
  top: 0;
  z-index: 1;
  opacity: 0;
  transition: opacity 150ms;
}
.image:hover .toggle-button {
  opacity: 1;
}
.image video {
  width: 100%;
  height: 100%;
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
}
</style>
