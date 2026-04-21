// Ambient module declarations for non-TS assets
// Fixes: TS(2882) "Cannot find module or type declarations for side-effect import of './globals.css'"
declare module "*.css";
declare module "*.scss";
declare module "*.sass";
declare module "*.module.css" {
  const classes: { readonly [key: string]: string };
  export default classes;
}
declare module "*.module.scss" {
  const classes: { readonly [key: string]: string };
  export default classes;
}
