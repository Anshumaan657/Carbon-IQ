import * as React from "react";
import { addPropertyControls, ControlType, useIsStaticRenderer } from "framer";
import CarbonIQ from "../apps/web/src/carboniq/CarbonIQ";

interface CarbonIQFramerProps {
  apiBaseUrl: string;
  mode: "demo" | "api";
  initialView: string;
  accent: string;
  style?: React.CSSProperties;
}

/**
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight auto
 */
export default function CarbonIQFramer(props: CarbonIQFramerProps) {
  const isStaticRenderer = useIsStaticRenderer();
  return <CarbonIQ {...props} staticMode={isStaticRenderer} />;
}

addPropertyControls(CarbonIQFramer, {
  mode: {
    type: ControlType.Enum,
    title: "Data mode",
    options: ["demo", "api"],
    optionTitles: ["Synthetic demo", "Live FastAPI"],
    defaultValue: "demo",
  },
  apiBaseUrl: {
    type: ControlType.String,
    title: "API base URL",
    defaultValue: "http://localhost:8000/api/v1",
    hidden: props => props.mode !== "api",
  },
  initialView: {
    type: ControlType.Enum,
    title: "Starting view",
    options: ["home", "catalogue", "preferences", "methodology"],
    optionTitles: ["Landing", "Catalogue", "Preferences", "Methodology"],
    defaultValue: "home",
  },
  accent: {
    type: ControlType.Color,
    title: "Signal color",
    defaultValue: "#C9F58A",
  },
});
