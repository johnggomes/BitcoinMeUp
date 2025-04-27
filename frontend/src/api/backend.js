export async function fetchOnboardingQuestions() {
  const response = await fetch("http://127.0.0.1:8000/onboarding-questions");
  if (!response.ok) {
    throw new Error("Failed to fetch onboarding questions");
  }
  return await response.json();
}
