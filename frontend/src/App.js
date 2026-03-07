import AboutSection from "./components/AboutSection";
import AnalyzerSection from "./components/AnalyzerSection";
import Footer from "./components/Footer";
import "./App.css";
function App() {
  return (
    <div className="app-wrapper">

      {/* 🌈 FLOATING BACKGROUND BUBBLES */}
      <div className="background-bubbles">
        <span></span>
        <span></span>
        <span></span>
        <span></span>
      </div>
    <>
    
      <AboutSection />
      
      <AnalyzerSection />
      <Footer/>
      
    </>
    </div>
  );
}
export default App;
