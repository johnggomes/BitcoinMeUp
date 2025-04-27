import { useState } from "react";
import WelcomePage from "./components/WelcomePage";
import OnboardingPage from "./components/OnboardingPage";
import ContentPage from "./components/ContentPage";
import ProgressTreePage from "./components/ProgressTreePage";

function App() {
  const [currentScreen, setCurrentScreen] = useState("welcome");

  const goToOnboarding = () => setCurrentScreen("onboarding");
  const goToContent = () => setCurrentScreen("content");
  const goToProgressTree = () => setCurrentScreen("progress");

  return (
    <div>
      {currentScreen === "welcome" && <WelcomePage onStart={goToOnboarding} />}
      {currentScreen === "onboarding" && (
        <OnboardingPage onComplete={goToContent} />
      )}
      {currentScreen === "content" && (
        <ContentPage goToProgress={goToProgressTree} />
      )}
      {currentScreen === "progress" && <ProgressTreePage />}
    </div>
  );
}

export default App;
