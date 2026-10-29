import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";

import InventoryDashboard from "./pages/InventoryDashboard";
import ProductPage from "./pages/ProductPage";
import Home from "./pages/Home";
import InventoryPage from "./pages/InventoryPage";
import ModelComparison from "./pages/ModelComparison";
import Sidebar from "./components/Sidebar";
import "@fontsource/inter";

function App() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "#020617" }}>

        {/* ✅ Sidebar with synchronized state */}
        <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

        {/* ✅ Main content */}
        <div
          style={{
            marginLeft: collapsed ? "80px" : "240px",
            width: "100%",
            transition: "0.3s",
            padding: "20px",
            background: "#020617",
            minHeight: "100vh"
          }}
        >
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/inventory" element={<InventoryPage />} />
            <Route path="/inventory/:id" element={<InventoryDashboard />} />
            <Route path="/product/:productId" element={<ProductPage />} />
            <Route path="/models" element={<ModelComparison />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
