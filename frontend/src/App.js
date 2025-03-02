import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Tickets from "./pages/Tickets";
import Upload from "./pages/Upload";
import Chatbot from "./pages/Chatbot";
import NewTicket from "./pages/NewTicket";
import Home from "./pages/Home";

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />  
        <Route path="/tickets" element={<Tickets />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/new-ticket" element={<NewTicket />} />
      </Routes>
    </>
  );
}

export default App;
