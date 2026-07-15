import mark from "../assets/brand/applymize-mark.svg";
import markLight from "../assets/brand/applymize-mark-light.svg";
import logo from "../assets/brand/applymize-logo.svg";

type BrandLogoProps = {
  variant?: "mark" | "horizontal" | "sidebar" | "auth";
  light?: boolean;
  className?: string;
};

export function BrandLogo({ variant = "sidebar", light = false, className = "" }: BrandLogoProps) {
  if (variant === "horizontal") {
    return <img src={logo} alt="Applymize" className={`h-14 w-auto ${className}`} />;
  }

  if (variant === "mark") {
    return <img src={light ? markLight : mark} alt="Applymize" className={`h-10 w-10 ${className}`} />;
  }

  if (variant === "auth") {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <img src={mark} alt="Applymize" className="h-14 w-14 rounded-2xl shadow-sm" />
        <div>
          <h1 className="text-xl font-black tracking-tight text-slate-950">Applymize</h1>
          <p className="text-xs font-semibold text-slate-500">IA que impulsiona sua carreira</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex min-w-0 items-center gap-3 ${className}`}>
      <img src={mark} alt="Applymize" className="h-10 w-10 shrink-0 rounded-2xl shadow-sm" />
      <div className="min-w-0">
        <h1 className="truncate text-base font-black tracking-tight text-slate-950">Applymize</h1>
        <p className="truncate text-xs font-semibold text-slate-500">IA que impulsiona sua carreira</p>
      </div>
    </div>
  );
}
