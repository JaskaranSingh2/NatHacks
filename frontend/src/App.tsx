import { useState, useEffect } from "react";
import "./App.css";

const URL = "http://localhost:8000";

function App() {
	const [health, setHealth] = useState(null);
	const [ws, setWs] = useState(false);

	useEffect(() => {
		fetch(`${URL}/health`)
			.then((r) => r.json())
			.then(setHealth)
			.catch(() => {});
		const socket = new WebSocket("ws://localhost:8000/ws");
		socket.onopen = () => setWs(true);
		socket.onclose = () => setWs(false);
		return () => socket.close();
	}, []);

	return (
		<div className="container">
			<h1>🏥 Assistive Coach</h1>
			<p>Status: {ws ? "✅ Connected" : "⭕ Disconnected"}</p>
			{health && (
				<div>
					<h2>Health</h2>
					<p>Camera: {health.camera}</p>
					<p>FPS: {health.fps?.toFixed(1)}</p>
				</div>
			)}
			<img
				src={`${URL}/preview.jpg`}
				alt="preview"
				style={{ maxWidth: "640px", border: "2px solid #00d1ff" }}
			/>
		</div>
	);
}

export default App;
