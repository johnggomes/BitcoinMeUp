function WelcomePage({ onStart }) {
  return (
    <div>
      <h1>Welcome to BitcoinMeUp</h1>
      <button onClick={onStart}>Start Onboarding</button>
    </div>
  );
}

export default WelcomePage;
