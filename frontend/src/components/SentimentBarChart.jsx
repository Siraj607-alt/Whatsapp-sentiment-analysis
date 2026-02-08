import {
    Chart as ChartJS,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
  } from "chart.js";
  import { Bar } from "react-chartjs-2";
  
  ChartJS.register(
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend
  );
  
  export default function SentimentBarChart({ counts }) {
    const data = {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          label: "Messages",
          data: [
            counts?.Positive || 0,
            counts?.Neutral || 0,
            counts?.Negative || 0
          ],
          backgroundColor: ["#4CAF50", "#FFC107", "#F44336"],
          borderRadius: 8,
          barThickness: 40   // 🔥 KEY FIX
        }
      ]
    };
  
    const options = {
      responsive: true,
      maintainAspectRatio: false, // 🔥 KEY FIX
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    };
  
    return (
      <div style={{ height: "260px", maxWidth: "600px", margin: "0 auto" }}>
        <Bar data={data} options={options} />
      </div>
    );
  }
  