import CarbonIQ from "../src/carboniq/CarbonIQ";
export default function Page() {
  return <CarbonIQ apiBaseUrl={process.env.NEXT_PUBLIC_CARBONIQ_API_URL || "http://localhost:8000/api/v1"} mode={process.env.NEXT_PUBLIC_CARBONIQ_MODE === "api" ? "api" : "demo"} />;
}
