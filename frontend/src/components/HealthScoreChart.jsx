import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function HealthScoreChart({ score }) {
  const data = {
    labels: ["Healthy", "Unhealthy"],
    datasets: [
      {
        data: [score, 100 - score],
        backgroundColor: ["#4CAF50", "#F44336"],
        borderWidth: 0
      }
    ]
  };

  const options = {
    cutout: "70%",
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    }
  };

  return (
    <div className="health-chart">
      <Doughnut data={data} options={options} />
      <div className="health-center">
        <span className="health-number">{score}</span>
        <span className="health-total">/100</span>
      </div>
    </div>
  );
}
