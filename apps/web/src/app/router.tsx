import { createBrowserRouter } from "react-router-dom";
import { Shell } from "../components/layout/Shell";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { NewScreeningPage } from "../features/screening/NewScreeningPage";
import { ProcessingPage } from "../features/screening/ProcessingPage";
import { CandidateReviewPage } from "../features/candidates/CandidateReviewPage";
import { ComparisonPage } from "../features/comparison/ComparisonPage";
import { HistoryPage } from "../features/history/HistoryPage";
import { SettingsPage } from "../features/settings/SettingsPage";
import { AnalyticsPage } from "../features/analytics/AnalyticsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Shell />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "screen/new",
        element: <NewScreeningPage />,
      },
      {
        path: "screen/processing",
        element: <ProcessingPage />,
      },
      {
        path: "screen/:runId/review",
        element: <CandidateReviewPage />,
      },
      {
        path: "screen/:runId/compare",
        element: <ComparisonPage />,
      },
      {
        path: "history",
        element: <HistoryPage />,
      },
      {
        path: "analytics",
        element: <AnalyticsPage />,
      },
      {
        path: "settings",
        element: <SettingsPage />,
      },
    ],
  },
]);
