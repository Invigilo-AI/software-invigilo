<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { nanoid } from "nanoid";
import _pick from "lodash/pick";
import _union from "lodash/union";
import _difference from "lodash/difference";

export type BoundaryShapeData = {
  type: "rectangle" | "ellipse" | "polygon" | "polyline" | "point";
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  points?: number[];
  closed?: boolean;
};
export type BoundaryData = {
  image: {
    file_name?: string;
    width: number;
    height: number;
  };
} & {
  [key: string]: BoundaryShapeData[];
};
export interface BoundaryEditorEmits {
  (e: "update:modelValue", value: BoundaryData): void;
  (e: "change", value: any): void;
}
export interface BoundaryEditorProps {
  image?: string;
  background?: string;
  size?: { width: number; height: number };
  modelValue?: BoundaryData;
  config?: any;
  responsive?: boolean;
  boundaryKey?: string;
  excludeTool?: string[];
  allowTool?: string[];
}
export interface MultiSelectOption {
  value: any;
  label: string;
}
export type BoundaryConfig = {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  points?: number[];
  rotation?: number;
  closed?: boolean;
  fillEnabled?: boolean;
  draggable?: boolean;
};
export type Point = {
  x: number;
  y: number;
};
export type KonvaMouseEvent = {
  type: string;
  target: any;
  evt: {
    x: number;
    y: number;
    clientX: number;
    clientY: number;
    layerX: number;
    layerY: number;
    movementX: number;
    movementY: number;
  };
  currentTarget: any;
};
export type Tool = {
  type: string;
  icon: string;
  label: string;
  disabled?: boolean;
  draggable?: boolean;
  mouseDown?: Function;
  mouseMove?: Function;
  mouseUp?: Function;
  click?: Function;
  dblClick?: Function;
  deactivate?: Function;
};
export type Boundary = {
  component: string;
  id: string;
  config: BoundaryConfig;
};
const emit = defineEmits<BoundaryEditorEmits>();
const props = withDefaults(defineProps<BoundaryEditorProps>(), {
  config: {
    minSize: {
      width: 10,
      height: 10,
    },
  },
  responsive: false,
  boundaryKey: "boundaries",
});

const selectedShape = ref<Boundary | null>(null);
const stage = ref();
const eventLayer = ref(null);
const rubberLayer = ref(null);
const drawLayer = ref();
const backgroundConfig = reactive({
  image: null,
  width: 0,
  height: 0,
  listening: false,
  draggable: false,
});
const stageConfig = reactive({
  width: 0,
  height: 0,
});
const eventRectConfig = reactive({
  x: 0,
  y: 0,
  width: 0,
  height: 0,
});
const boundaries = ref<Boundary[]>([]);
const boundaryFields = (componentType: string) => {
  const commonFields = [
    "x",
    "y",
    "width",
    "height",
    "points",
    "rotation",
    "meta",
  ];
  const excludeFields =
    {
      "v-camera": ["width", "height"],
    }[componentType] || [];
  const includeFields =
    {
      "v-ring": ["points"],
      "v-camera": ["angle", "range"],
    }[componentType] || [];

  return _union(_difference(commonFields, excludeFields), includeFields);
};
const defaultDrawConfig = reactive({
  fill: "#00aa0040",
  fillEnabled: true,
  stroke: "#00cc00",
  strokeWidth: 2,
  hitStrokeWidth: 6,
  shadowEnabled: false,
  listening: false,
  draggable: false,
  innerRadius: 2,
  outerRadius: 4,
  offset: {
    x: 0,
    y: 0,
  },
});
const defaultRubberConfig = reactive({
  fill: "#00aa0040",
  fillEnabled: true,
  stroke: "#00cc00",
  strokeWidth: 2,
  hitStrokeWidth: 6,
  shadowEnabled: false,
  listening: false,
  draggable: false,
  dash: [2, 2],
});

const transformerConfig = reactive({
  rotationSnaps: [0, 45, 90, 135, 180, 225, 270, 315],
  shouldOverdrawWholeArea: true,
  enabledAnchors: [
    "top-left",
    "top-center",
    "top-right",
    "middle-right",
    "middle-left",
    "bottom-left",
    "bottom-center",
    "bottom-right",
  ],
});
const rubberRect = ref();
const rubberEllipse = ref();
const rubberLine = ref();
const rubberRectConfig = reactive({
  x: 0,
  y: 0,
  width: 0,
  height: 0,
});
const rubberEllipseConfig = reactive({
  x: 0,
  y: 0,
  width: 0,
  height: 0,
});
const rubberLineConfig = reactive<BoundaryConfig>({
  points: [],
  fillEnabled: false,
  closed: false,
});
const drawProps = reactive({
  type: "rect",
  mode: "",
  startPoint: { x: 0, y: 0 },
  currentPoint: { x: 0, y: 0 },
  endPoint: { x: 0, y: 0 },
});
const tools = reactive<Tool[]>([
  {
    type: "select",
    icon: "carbon:cursor-2",
    label: "Select",
    deactivate: () => {
      selectedShape.value = null;
    },
  },
  {
    type: "point",
    icon: "gis:point",
    label: "Point",
    click: () => {
      const { x, y } = drawProps.endPoint;
      addBoundary("v-ring", {
        x,
        y,
      });
    },
  },
  {
    type: "rect",
    icon: "gis:rectangle-pt",
    label: "Rectangle",
    draggable: true,
    mouseMove: () => {
      if (drawProps.mode !== "dragging") return;
      const posRect = reverse(drawProps.startPoint, drawProps.endPoint);
      const rubberNode = rubberRect.value.getNode();

      rubberNode.x(posRect.x1);
      rubberNode.y(posRect.y1);
      rubberNode.width(posRect.x2 - posRect.x1);
      rubberNode.height(posRect.y2 - posRect.y1);
      rubberNode.visible(true);
    },
    mouseUp: () => {
      const rubberNode = rubberRect.value.getNode();

      if (!rubberNode.visible()) return;

      rubberNode.visible(false);

      const x = rubberNode.x();
      const y = rubberNode.y();
      const width = rubberNode.width();
      const height = rubberNode.height();

      if (
        width < props.config.minSize.width ||
        height < props.config.minSize.height
      )
        return;

      addBoundary("v-rect", { x, y, width, height });
    },
  },
  {
    type: "ellipse",
    icon: "mdi:ellipse-outline",
    label: "Ellipse",
    draggable: true,
    mouseMove: () => {
      if (drawProps.mode !== "dragging") return;
      const posRect = reverse(drawProps.startPoint, drawProps.endPoint);
      const rubberNode = rubberEllipse.value.getNode();

      const width = Math.abs(posRect.x2 - posRect.x1);
      const height = Math.abs(posRect.y2 - posRect.y1);

      rubberNode.x(posRect.x1 + width / 2);
      rubberNode.y(posRect.y1 + height / 2);
      rubberNode.width(width);
      rubberNode.height(height);
      rubberNode.visible(true);
    },
    mouseUp: () => {
      const rubberNode = rubberEllipse.value.getNode();

      if (!rubberNode.visible()) return;

      rubberNode.visible(false);

      const x = rubberNode.x();
      const y = rubberNode.y();
      const width = rubberNode.width();
      const height = rubberNode.height();

      if (
        width < props.config.minSize.width ||
        height < props.config.minSize.height
      )
        return;
      addBoundary("v-ellipse", { x, y, width, height });
    },
  },
  {
    type: "polygon",
    icon: "ph:polygon-light",
    label: "Polygon",
    draggable: true,
    mouseDown: () => {
      const rubberNode = rubberLine.value.getNode();
      rubberNode.visible(true);

      if (!rubberLineConfig.points) return;

      const { x, y } = drawProps.startPoint;
      if (!rubberLineConfig.points.length) {
        rubberLineConfig.points.push(x, y, x, y);
        rubberLineConfig.closed = false;
        rubberLineConfig.fillEnabled = false;
      } else {
        rubberLineConfig.points.push(x, y);
        rubberLineConfig.closed = true;
        rubberLineConfig.fillEnabled = true;
      }
    },
    mouseMove: () => {
      if (!rubberLineConfig.points) return;
      if (drawProps.mode !== "dragging" && !rubberLineConfig.points.length)
        return;
      const posRect = reverse(drawProps.startPoint, drawProps.endPoint);

      const { x, y } = drawProps.currentPoint;
      rubberLineConfig.points.splice(-2, 2, x, y);
    },
    mouseUp: () => {
      if (!rubberLineConfig.points) return;
      if (!rubberLineConfig.points.length) {
        const { x, y } = drawProps.currentPoint;
        rubberLineConfig.points.push(x, y);
      }
    },
    dblClick: () => {
      if (!rubberLineConfig.points) return;
      if (rubberLineConfig.points.length - 4 < 6) return;

      const rubberNode = rubberLine.value.getNode();
      rubberNode.visible(false);
      rubberLineConfig.points.splice(-4, 4);

      addBoundary("v-line", {
        points: [...rubberLineConfig.points],
        closed: true,
      });

      rubberLineConfig.points = [];
      rubberLineConfig.closed = false;
      rubberLineConfig.fillEnabled = false;
    },
  },
  {
    type: "path",
    icon: "gis:polyline-pt",
    label: "Path line",
    mouseDown: () => {
      const rubberNode = rubberLine.value.getNode();
      rubberNode.visible(true);

      if (!rubberLineConfig.points) return;

      const { x, y } = drawProps.startPoint;
      if (!rubberLineConfig.points.length) {
        rubberLineConfig.points.push(x, y, x, y);
      } else {
        rubberLineConfig.points.push(x, y);
      }
    },
    mouseMove: () => {
      if (!rubberLineConfig.points) return;

      if (drawProps.mode !== "dragging" && !rubberLineConfig.points.length)
        return;
      const { x, y } = drawProps.currentPoint;
      rubberLineConfig.points.splice(-2, 2, x, y);
    },
    dblClick: () => {
      if (!rubberLineConfig.points) return;
      if (rubberLineConfig.points.length - 4 < 4) return;

      rubberLineConfig.points.splice(-4, 4);

      const rubberNode = rubberLine.value.getNode();
      rubberNode.visible(false);

      addBoundary("v-line", { points: [...rubberLineConfig.points] });

      rubberLineConfig.points = [];
    },
  },
  {
    type: "camera",
    icon: "carbon:video-add",
    label: "Camera",
    disabled: true,
    click: () => {
      const { x, y } = drawProps.endPoint;
      // addBoundary("v-camera", { x, y });
      addBoundary("v-camera", {
        x: x - 12,
        y: y + 16,
      });
    },
  },
]);
const availableTools = computed(() =>
  tools.filter(
    ({ type, disabled = false }) =>
      (disabled && props.allowTool?.includes(type)) ||
      !props.excludeTool?.includes(type)
  )
);
const currentTool = ref<Tool>(availableTools.value[0] || { type: "none" });
const transformer = ref();
const isSelectTool = computed(() => currentTool.value.type === "select");

const applyBackground = () => {
  if (props.background) {
    const image = new Image();
    image.onload = function () {
      const { width, height } = this as any;

      (backgroundConfig.image as HTMLImageElement | null) = image;

      backgroundConfig.width = width;
      backgroundConfig.height = height;

      stageConfig.width = width;
      stageConfig.height = height;

      eventRectConfig.width = width;
      eventRectConfig.height = height;

      fitStageIntoParentContainer(width, height);
    };
    image.src = props.background;
  } else if (!(props.size && "width" in props.size && "height" in props.size)) {
    stageConfig.width = 0;
    stageConfig.height = 0;

    fitStageIntoParentContainer(0, 0);
  }
};
const applyModelValue = () => {
  if (props.modelValue && props.modelValue[props.boundaryKey]) {
    boundaries.value = (props.modelValue[props.boundaryKey] || []).map(
      (data) => {
        const id = nanoid(6);
        const component = typeToComponent(data.type);
        const config = {
          name: id,
          ..._pick(data, boundaryFields(component)),
        };

        if (data.type === "polygon") {
          config.closed = true;
        }

        return {
          id,
          component,
          config,
        };
      }
    );
    selectedShape.value = null;
    // updateTransformer()
  }
};

watch(() => props.background, applyBackground);

onMounted(() => {
  applyBackground();
  applyModelValue();
});

watch(
  () => props.size,
  () => {
    if (props.size && "width" in props.size && "height" in props.size) {
      const { width, height } = props.size;

      stageConfig.width = width;
      stageConfig.height = height;

      eventRectConfig.width = width;
      eventRectConfig.height = height;

      fitStageIntoParentContainer(width, height);
    }
  }
);

watch(() => props.modelValue, applyModelValue);

watch(
  () => selectedShape.value,
  () => {
    updateTransformer();
  }
);

const parentStage = ref<HTMLElement | null>(null);
const stageScale = ref({ x: 1, y: 1 });
const fitStageIntoParentContainer = (
  sceneWidth: number,
  sceneHeight: number
) => {
  const container = parentStage.value;
  if (!container || !props.responsive) return;

  const containerWidth = container.offsetWidth;
  const containerHeight = container.offsetHeight || containerWidth;

  if (containerWidth < sceneWidth) {
    stageScale.value.x = containerWidth / sceneWidth;
    stageScale.value.y = stageScale.value.x;
    // stageScale.value.y = containerHeight / sceneHeight;
    const width = sceneWidth * stageScale.value.x;
    const height = sceneHeight * stageScale.value.y;

    container.style.height = `${height}px`;
  } else {
    container.style.height = "";

    stageScale.value.x = 1;
    stageScale.value.y = 1;
  }
  // transformer.value.getNode().scale({ x: stageScale.value.x, y: stageScale.value.y });
  // drawLayer.value.getNode().scale({ x: 1/stageScale.value.x, y: 1/stageScale.value.y });

  stage.value.getNode().width(sceneWidth * stageScale.value.x);
  stage.value.getNode().height(sceneHeight * stageScale.value.y);
  stage.value.getNode().scale({ x: stageScale.value.x, y: stageScale.value.y });
};

const eventLog = ({ type, target, evt, currentTarget }: KonvaMouseEvent) => {
  const { x, y, clientX, clientY, layerX, layerY, movementX, movementY } = evt;
  console.info(`${type}`, layerX, layerY);
};
const updateEventScale = (e: KonvaMouseEvent) => {
  return {
    ...e,
    evt: {
      ...e.evt,
      layerX: e.evt.layerX * (1 / stageScale.value.x),
      layerY: e.evt.layerY * (1 / stageScale.value.y),
    },
  };
};

const onMouseDown = (e: KonvaMouseEvent) => {
  // eventLog(e);
  const event = updateEventScale(e);
  const { layerX: x, layerY: y } = event.evt;
  drawProps.startPoint.x = x;
  drawProps.startPoint.y = y;
  drawProps.currentPoint.x = x;
  drawProps.currentPoint.y = y;
  drawProps.endPoint.x = x;
  drawProps.endPoint.y = y;

  if (currentTool.value.draggable) {
    drawProps.mode = "dragging";
  }

  if (currentTool.value.mouseDown) currentTool.value.mouseDown(event);

  stage.value.getNode().draw();
};
const onMouseMove = (e: KonvaMouseEvent) => {
  // eventLog(e)
  const event = updateEventScale(e);
  const { layerX: x, layerY: y } = event.evt;

  drawProps.currentPoint.x = x;
  drawProps.currentPoint.y = y;

  if (drawProps.mode === "dragging") {
    drawProps.endPoint.x = x;
    drawProps.endPoint.y = y;
  }

  if (currentTool.value.mouseMove) currentTool.value.mouseMove(event);

  stage.value.getNode().draw();
};
const onMouseUp = (e: KonvaMouseEvent) => {
  //   eventLog(e);

  const event = updateEventScale(e);
  if (currentTool.value.draggable) {
    drawProps.mode = "";
  }

  if (currentTool.value.mouseUp) currentTool.value.mouseUp(event);

  stage.value.getNode().draw();
};
const onDblClick = (e: KonvaMouseEvent) => {
  //   eventLog(e);

  const event = updateEventScale(e);
  if (currentTool.value.draggable) {
    drawProps.mode = "";
  }

  if (currentTool.value.dblClick) currentTool.value.dblClick(event);

  stage.value.getNode().draw();
};
const onClick = (e: KonvaMouseEvent) => {
  //   eventLog(e);
  const event = updateEventScale(e);
  if (currentTool.value.click) currentTool.value.click(event);

  stage.value.getNode().draw();
};
const events = {
  mousedown: onMouseDown,
  mousemove: onMouseMove,
  mouseup: onMouseUp,
  dblclick: onDblClick,
  click: onClick,
};
function reverse(r1: Point, r2: Point) {
  var r1x = r1.x,
    r1y = r1.y,
    r2x = r2.x,
    r2y = r2.y,
    d;
  if (r1x > r2x) {
    d = Math.abs(r1x - r2x);
    r1x = r2x;
    r2x = r1x + d;
  }
  if (r1y > r2y) {
    d = Math.abs(r1y - r2y);
    r1y = r2y;
    r2y = r1y + d;
  }
  return { x1: r1x, y1: r1y, x2: r2x, y2: r2y }; // return the corrected rect.
}
const selectTool = (tool: Tool) => {
  if (currentTool.value.deactivate) currentTool.value.deactivate();
  currentTool.value = tool;
};

const handleTransformStart = (e: KonvaMouseEvent) => {
  console.log("handleTransformStart", e);
};

const handleTransform = (e: KonvaMouseEvent) => {
  console.log("handleTransform", e);
};
const handleTransformEnd = (e: KonvaMouseEvent) => {
  console.log("handleTransformEnd");

  const shape = boundaries.value.find((shape) => shape === selectedShape.value);
  if (!shape) return;

  const updateConfig: BoundaryConfig = {
    rotation: e.target.rotation(),
    x: e.target.x(),
    y: e.target.y(),
  };

  const scaleX = e.target.scaleX();
  const scaleY = e.target.scaleY();

  if (shape.component === "v-line" && shape.config.points) {
    const points = [];
    for (var i = 0; i < shape.config.points.length / 2; i++) {
      const x = shape.config.points[i * 2] * scaleX;
      const y = shape.config.points[i * 2 + 1] * scaleY;
      points.push(x, y);
    }

    updateConfig.points = points;
  } else {
    updateConfig.x = e.target.x();
    updateConfig.y = e.target.y();
    updateConfig.width = (shape.config.width || 1) * scaleX;
    updateConfig.height = (shape.config.height || 1) * scaleY;
  }

  updateBoundary(shape.id, updateConfig);

  e.target.scaleX(1);
  e.target.scaleY(1);
};
const handleDragEnd = (e: KonvaMouseEvent) => {
  const shape = boundaries.value.find((shape) => shape === selectedShape.value);
  if (!shape) return;
  const x = e.target.x();
  const y = e.target.y();

  updateBoundary(shape.id, { x, y });
};

const handleStageMouseDown = (e: KonvaMouseEvent) => {
  if (currentTool.value.type !== "select") return;

  if (e.target instanceof Node) return;

  if (e.target === stage.value.getNode().getStage()) {
    selectedShape.value = null;
    return;
  }

  // clicked on transformer - do nothing
  const clickedOnTransformer =
    e.target && e.target.getParent().getClassName() === "Transformer";
  if (clickedOnTransformer) {
    return;
  }

  // find clicked rect by its id
  const id = e.target.name();
  const shape = boundaries.value.find((r) => r.id === id);
  if (shape) {
    selectedShape.value = shape;
    shape.config.draggable = true;
  } else {
    selectedShape.value = null;
  }
};

const selectNodeById = (id?: string | null) =>
  transformer.value
    .getNode()
    .getStage()
    .find((node: any) => id && node.name() === id);

const updateTransformer = () => {
  const transformerNode = transformer.value.getNode();
  const stage = transformerNode.getStage();

  const selectedNode = selectNodeById(
    selectedShape.value && selectedShape.value.id
  );

  // do nothing if selected node is already attached
  if (selectedNode === transformerNode.node()) {
    return;
  }
  if (selectedNode && selectedShape.value) {
    transformerNode.nodes(selectedNode);

    if (["v-ring", "v-camera"].includes(selectedShape.value.component)) {
      transformerNode.resizeEnabled(false);
      transformerNode.anchorCornerRadius(5);
    } else {
      transformerNode.resizeEnabled(true);
      transformerNode.anchorCornerRadius(0);
    }
  } else {
    transformerNode.nodes([]);
  }

  transformerNode.forceUpdate();
};
const handleMouseOver = () => {
  //   defaultDrawConfig.strokeWidth = 4;
};
const handleMouseOut = () => {
  //   defaultDrawConfig.strokeWidth = 2;
};
const addBoundary = (component: string, data: BoundaryConfig) => {
  const id = nanoid(6);
  const config = {
    name: id,
    ...data,
  };
  boundaries.value.push({
    id,
    component,
    config,
  });

  updateModelValue();
};
const updateBoundary = (id: string, data: BoundaryConfig) => {
  const shape = boundaries.value.find((elm) => elm.id === id);

  if (!shape) return;
  shape.config = { ...shape.config, ...data };

  updateModelValue();
};
const componentToType = (component: string, closed: boolean = false) =>
  ({
    "v-rect": "rectangle",
    "v-ellipse": "ellipse",
    "v-line": closed ? "polygon" : "polyline",
    "v-ring": "point",
    "v-camera": "camera",
  }[component]);

const typeToComponent = (type: string) =>
  ({
    rectangle: "v-rect",
    ellipse: "v-ellipse",
    polygon: "v-line",
    polyline: "v-line",
    point: "v-ring",
    camera: "v-camera",
  }[type] || "v-rect");

const typeToKonvaComponent = (type: string, config: any) => {
  const isComponent =
    {
      "v-camera": "v-shape",
    }[type] || type;

  const withConfig =
    {
      "v-camera": {
        sceneFunc: function (ctx: CanvasRenderingContext2D, shape: any) {
          const center = {
            x: 16,
            y: 12,
          };

          const angle = ((shape.attrs?.angle || 45) * Math.PI) / 180;
          const range = shape.attrs?.range || 100;

          const beginAngle = -angle / 2;
          const endAngle = beginAngle + angle;
          const medianAngle = (endAngle + beginAngle) / 2;
          const offsetX = Math.cos(medianAngle);
          const offsetY = Math.sin(medianAngle);

          const grd = ctx.createRadialGradient(
            center.x,
            center.y,
            0,
            center.x,
            center.y,
            range
          );
          grd.addColorStop(0, "lime");
          grd.addColorStop(1, "transparent");

          ctx.shadowBlur = 0;
          ctx.fillStyle = grd;

          ctx.rotate((-90 * Math.PI) / 180);

          ctx.beginPath();
          ctx.moveTo(center.x + offsetX, center.y + offsetY);
          ctx.arc(
            center.x + offsetX,
            center.y + offsetY,
            range,
            beginAngle,
            endAngle
          );
          ctx.lineTo(center.x + offsetX, center.y + offsetY);
          ctx.stroke();
          ctx.rect(center.x - 10, center.y - 5, 10, 10);
          ctx.fill();
          // special Konva.js method
          // @ts-ignore
          ctx.fillShape(shape);
          // ctx.fillStrokeShape(shape);

          ctx.beginPath();
          ctx.moveTo(17, 10.5);
          ctx.lineTo(17, 6);
          ctx.lineTo(3, 6);
          ctx.lineTo(3, 18);
          ctx.lineTo(17, 18);
          ctx.lineTo(17, 13.5);
          ctx.lineTo(21, 17.5);
          ctx.lineTo(21, 6.5);
          ctx.lineTo(17, 10.5);
          ctx.closePath();
          ctx.shadowBlur = 5;
          ctx.shadowColor = "white";
          ctx.fillStyle = "black";
          ctx.strokeStyle = "lime";
          ctx.fill();
          // ctx.fillShape(shape);
          // ctx.fillStrokeShape(shape);

          shape.getSelfRect = function () {
            return {
              x: 7,
              y: -16,
              width: 10,
              height: 10,
            };
          };
        },
      },
    }[type] || {};

  return { component: isComponent, config: { ...withConfig, ...config } };
};

const updateModelValue = () => {
  const data = boundaries.value.map(({ component, config }) => {
    const type = componentToType(component, config.closed);
    return <BoundaryShapeData>{
      type,
      ..._pick(config, boundaryFields(component)),
    };
  });
  const { width, height } = stageConfig;
  const value = {
    image: {
      // @ts-ignore
      file_name: props.image || props.background,
      width,
      height,
    },
    [props.boundaryKey]: data,
  };
  // @ts-ignore
  emit("update:modelValue", value);
  emit("change", value);
};
const removeShape = (id: string) => {
  const shapeIndex = getShapeIndexById(id);
  boundaries.value.splice(shapeIndex, 1);
  selectedShape.value = null;
  updateModelValue();
};
const getShapeById = (id: string) => {
  return <Boundary>boundaries.value.find((elm) => elm.id === id);
};
const getShapeIndexById = (id: string) => {
  return <number>boundaries.value.findIndex((elm) => elm.id === id);
};
</script>
<template>
  <VField addons>
    <VControl :key="tool.type" v-for="tool in availableTools">
      <VButton
        :icon="tool.icon"
        :lower="tool.type === currentTool.type"
        :color="(tool.type === currentTool.type && 'primary') || undefined"
        @click="selectTool(tool)"
        >{{ tool.label }}</VButton
      >
    </VControl>
  </VField>
  <div
    :class="[props.responsive && 'konva-stage-responsive']"
    ref="parentStage"
  >
    <v-stage
      :config="stageConfig"
      ref="stage"
      @mousedown="handleStageMouseDown"
      @touchstart="handleStageMouseDown"
    >
      <v-layer>
        <v-image :config="backgroundConfig" />
      </v-layer>
      <v-layer ref="drawLayer">
        <component
          :is="typeToKonvaComponent(component, config).component"
          :key="id"
          v-for="{ id, component, config } in boundaries"
          :config="{
            ...defaultDrawConfig,
            ...typeToKonvaComponent(component, config).config,
            listening: isSelectTool,
            draggable: isSelectTool,
          }"
          @transformstart="handleTransformStart"
          @transform="handleTransform"
          @transformend="handleTransformEnd"
          @dragend="handleDragEnd"
          @mouseover="handleMouseOver"
          @mouseout="handleMouseOut"
        />
        <v-transformer ref="transformer" :config="transformerConfig" />
      </v-layer>
      <v-layer ref="eventLayer" v-if="currentTool.type !== 'select'">
        <v-rect :config="eventRectConfig" v-on="events" />
      </v-layer>
      <v-layer ref="rubberLayer" v-if="currentTool.type !== 'select'">
        <v-rect
          :config="{ ...defaultRubberConfig, ...rubberRectConfig }"
          ref="rubberRect"
        />
        <v-ellipse
          :config="{ ...defaultRubberConfig, ...rubberEllipseConfig }"
          ref="rubberEllipse"
        />
        <v-line
          :config="{ ...defaultRubberConfig, ...rubberLineConfig }"
          ref="rubberLine"
        />
      </v-layer>
    </v-stage>
  </div>
  <br />
  <slot
    name="transform"
    v-if="selectedShape"
    :shape="selectedShape"
    :type="
      componentToType(selectedShape.component, selectedShape.config.closed)
    "
    :change="updateModelValue"
    :remove="removeShape"
  >
    <VField addons>
      <VControl>
        <VButton static>{{
          componentToType(selectedShape.component, selectedShape.config.closed)
        }}</VButton>
      </VControl>
      <VControl expanded>
        <input
          type="text"
          class="input"
          placeholder="Shape name"
          v-model="selectedShape.config.meta"
          @change="updateModelValue"
        />
      </VControl>
      <VControl>
        <VButton color="danger" @click="removeShape(selectedShape.id)"
          >Delete</VButton
        >
      </VControl>
    </VField>
  </slot>

  <!-- <code>{{ JSON.stringify(selectedShape?.config, null, 2) }}</code> -->
  <!-- <br /> -->
  <!-- <code>{{ JSON.stringify(rubberLineConfig, null, 2) }}</code> -->
  <!-- <br /> -->
  <!-- <code>{{ JSON.stringify(boundaries, null, 2) }}</code> -->
  <!-- <template :key="shape.id" v-for="shape in boundaries">
  <VField addons>
      <VControl>
          <input type="text" class="input" v-model="shape.id" readonly>
      </VControl>
      <VButton color="danger">Delete</VButton>
  </VField>
  </template> -->
</template>
<style lang="postcss">
.konva-stage-responsive {
  max-width: 100%;
  max-height: 100%;
  overflow: hidden;
}
</style>
