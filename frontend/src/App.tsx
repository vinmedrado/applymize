import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import { Layout } from "./components/Layout";
import { PageLoading } from "./components/Loading";
import { PrivateAccessNotice } from "./components/PrivateAccessNotice";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { hasPrivateBackendAccess } from "./services/api";

const Login = lazy(() => import("./pages/Login").then((module) => ({ default: module.Login })));
const Register = lazy(() => import("./pages/Register").then((module) => ({ default: module.Register })));
const ResetPassword = lazy(() => import("./pages/ResetPassword").then((module) => ({ default: module.ResetPassword })));
const Landing = lazy(() => import("./pages/Landing").then((module) => ({ default: module.Landing })));
const Demo = lazy(() => import("./pages/Demo").then((module) => ({ default: module.Demo })));
const LinkedInAnalyzer = lazy(() => import("./pages/LinkedInAnalyzer").then((module) => ({ default: module.LinkedInAnalyzer })));
const PrivateLinkedInAnalyzer = lazy(() => import("./pages/LinkedInAnalyzer").then((module) => ({ default: module.PrivateLinkedInAnalyzer })));
const HowItWorks = lazy(() => import("./pages/HowItWorks").then((module) => ({ default: module.HowItWorks })));
const PublicAtsLab = lazy(() => import("./pages/PublicAtsLab").then((module) => ({ default: module.PublicAtsLab })));
const Dashboard = lazy(() => import("./pages/Dashboard").then((module) => ({ default: module.Dashboard })));
const Jobs = lazy(() => import("./pages/Jobs").then((module) => ({ default: module.Jobs })));
const JobDetail = lazy(() => import("./pages/JobDetail").then((module) => ({ default: module.JobDetail })));
const Applications = lazy(() => import("./pages/Applications").then((module) => ({ default: module.Applications })));
const ApplicationAgent = lazy(() => import("./pages/ApplicationAgent").then((module) => ({ default: module.ApplicationAgent })));
const Profile = lazy(() => import("./pages/Profile").then((module) => ({ default: module.Profile })));
const AtsAnalyzer = lazy(() => import("./pages/AtsAnalyzer").then((module) => ({ default: module.AtsAnalyzer })));
const Notifications = lazy(() => import("./pages/Notifications").then((module) => ({ default: module.Notifications })));
const WhatsAppPairing = lazy(() => import("./pages/WhatsAppPairing").then((module) => ({ default: module.WhatsAppPairing })));
const Radar = lazy(() => import("./pages/Radar").then((module) => ({ default: module.Radar })));
const SkillGap = lazy(() => import("./pages/SkillGap").then((module) => ({ default: module.SkillGap })));
const Analytics = lazy(() => import("./pages/Analytics").then((module) => ({ default: module.Analytics })));
const Automation = lazy(() => import("./pages/Automation").then((module) => ({ default: module.Automation })));
const ApplymizeFit = lazy(() => import("./pages/ApplymizeFit").then((module) => ({ default: module.ApplymizeFit })));
const Billing = lazy(() => import("./pages/Billing").then((module) => ({ default: module.Billing })));
const AdminAnalytics = lazy(() => import("./pages/AdminAnalytics").then((module) => ({ default: module.AdminAnalytics })));
const RecruiterPanel = lazy(() => import("./pages/RecruiterPanel").then((module) => ({ default: module.RecruiterPanel })));
const AdvancedCV = lazy(() => import("./pages/AdvancedCV").then((module) => ({ default: module.AdvancedCV })));

export default function App() {
  const privateBackendAvailable = hasPrivateBackendAccess();

  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Suspense fallback={<PageLoading label="Carregando Applymize..." />}>
            <Routes>
              <Route path="/login" element={privateBackendAvailable ? <Login /> : <PrivateAccessNotice />} />
              <Route path="/register" element={privateBackendAvailable ? <Register /> : <PrivateAccessNotice />} />
              <Route path="/reset-password" element={privateBackendAvailable ? <ResetPassword /> : <PrivateAccessNotice />} />
              <Route path="/" element={<Landing />} />
              <Route path="/demo" element={<Demo />} />
              <Route path="/pricing" element={<Navigate to="/como-funciona" replace />} />
              <Route path="/linkedin-analyzer" element={<LinkedInAnalyzer />} />
              <Route path="/como-funciona" element={<HowItWorks />} />
              <Route path="/por-tras" element={<HowItWorks />} />
              <Route path="/laboratorio-ats" element={<PublicAtsLab />} />

              <Route element={<ProtectedRoute />}>
                <Route element={<Layout />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/jobs" element={<Jobs />} />
                  <Route path="/jobs/:jobId" element={<JobDetail />} />
                  <Route path="/applications" element={<Applications />} />
                  <Route path="/application-agent" element={<ApplicationAgent />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/ats-analyzer" element={<AtsAnalyzer />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/skill-gap" element={<SkillGap />} />
                  <Route path="/radar" element={<Radar />} />
                  <Route path="/notifications" element={<Notifications />} />
                  <Route path="/automation" element={<Automation />} />
                  <Route path="/whatsapp-pairing" element={<WhatsAppPairing />} />
                  <Route path="/app/linkedin-analyzer" element={<PrivateLinkedInAnalyzer />} />
                  <Route path="/applymize-fit" element={<ApplymizeFit />} />
                  <Route path="/billing" element={<Billing />} />
                  <Route path="/admin" element={<AdminAnalytics />} />
                  <Route path="/recruiter" element={<RecruiterPanel />} />
                  <Route path="/cv-pro" element={<AdvancedCV />} />
                </Route>
              </Route>

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
