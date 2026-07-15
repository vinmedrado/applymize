import { useEffect, useState } from "react";
import { CheckCircle2, CreditCard, Loader2, Lock, Sparkles, Zap } from "lucide-react";
import { getBillingPlans, getSubscription, Plan, startCheckout } from "../services/billing";
import { useToast } from "../context/ToastContext";
import { MiniFeature, PremiumHero, PremiumMetric, PremiumPanel } from "../components/Premium";

export function Billing() {
  const toast = useToast();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [planData, subData] = await Promise.all([getBillingPlans(), getSubscription()]);
      setPlans(planData.plans);
      setSubscription(subData);
    } catch {
      toast.error("Erro ao carregar billing", "Verifique a API.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function upgrade(code: string) {
    const result = await startCheckout(code);
    toast.success("Billing", result.message || "Checkout iniciado.");
    if (result.checkout_url) window.location.href = result.checkout_url;
    await load();
  }

  if (loading) return <div className="premium-card flex items-center gap-3 p-6"><Loader2 className="animate-spin" /> Carregando billing...</div>;

  return (
    <div className="space-y-6">
      <PremiumHero
        eyebrow="Stripe Ready"
        title="Planos, assinatura e monetização preparados para operação SaaS."
        description="Controle o plano atual, teste checkout em modo seguro e evolua para cobrança real com Stripe sem alterar a experiência principal do usuário."
        icon={CreditCard}
      >
        <div className="rounded-3xl border border-white/15 bg-white/10 p-4 text-white backdrop-blur lg:min-w-[340px]">
          <p className="text-xs font-black uppercase tracking-wide text-blue-100">Plano atual</p>
          <p className="mt-2 text-3xl font-black">{subscription?.plan?.name || "Free"}</p>
          <p className="mt-1 text-sm text-blue-100">Modo {subscription?.mode || "demo"}</p>
        </div>
      </PremiumHero>

      <div className="grid gap-4 md:grid-cols-3">
        <PremiumMetric label="Plano" value={subscription?.plan?.name || "Free"} helper="Controle comercial do tenant" />
        <PremiumMetric label="Modo" value={subscription?.mode || "demo"} helper="Seguro para portfólio e demonstração" />
        <PremiumMetric label="Billing" value="Stripe" helper="Checkout e webhook preparados" trend="Ready" />
      </div>

      <PremiumPanel title="Escolha um plano" subtitle="Cards preparados para venda direta, assinatura e diferenciação por feature.">
        <div className="grid gap-5 lg:grid-cols-4">
          {plans.map((plan) => (
            <section key={plan.code} className={`rounded-3xl border bg-white p-5 shadow-sm ${plan.code === "pro" ? "border-blue-500 ring-2 ring-blue-100" : "border-slate-200"}`}>
              <div className="flex items-center justify-between gap-3">
                <CreditCard className="h-6 w-6 text-blue-700" />
                {plan.code === subscription?.plan_code && <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-black text-emerald-700">Atual</span>}
              </div>
              <h2 className="mt-4 text-xl font-black text-slate-950">{plan.name}</h2>
              <p className="mt-2 min-h-10 text-sm leading-6 text-slate-600">{plan.description}</p>
              <p className="mt-4 text-3xl font-black text-slate-950">{plan.monthly_price === null ? "Custom" : `R$${plan.monthly_price}`}</p>
              <div className="mt-4 space-y-2">
                {plan.features.map((f) => <p key={f} className="flex gap-2 text-sm text-slate-700"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> {f}</p>)}
              </div>
              <button className="btn-primary mt-5 w-full" onClick={() => upgrade(plan.code)} disabled={plan.code === subscription?.plan_code}>
                {plan.code === subscription?.plan_code ? "Plano atual" : "Ativar"}
              </button>
            </section>
          ))}
        </div>
      </PremiumPanel>

      <div className="grid gap-4 md:grid-cols-3">
        <MiniFeature icon={Lock} title="Modo seguro" description="Sem chaves reais, o checkout permanece mockado e não processa cobrança." />
        <MiniFeature icon={Zap} title="Upgrade rápido" description="Com Price IDs e webhook, a camada fica pronta para produção." />
        <MiniFeature icon={Sparkles} title="Planos por feature" description="IA, LinkedIn Analyzer, Fit e Recruiter podem ter limites por plano." />
      </div>
    </div>
  );
}
