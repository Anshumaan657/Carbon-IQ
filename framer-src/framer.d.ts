/**
 * Local editor declarations for Framer code components.
 *
 * The Framer editor provides this module at runtime. It is intentionally not
 * added as an npm dependency to the standalone Next.js application.
 */
declare module "framer" {
  type PropertyControl = {
    type: unknown
    title?: string
    description?: string
    defaultValue?: unknown
    options?: readonly unknown[]
    optionTitles?: readonly string[]
    hidden?: (props: Record<string, any>) => boolean
  }

  export const ControlType: {
    Enum: unknown
    String: unknown
    Color: unknown
  }

  export function addPropertyControls(
    component: (...args: any[]) => any,
    controls: Record<string, PropertyControl>,
  ): void

  export function useIsStaticRenderer(): boolean
}
