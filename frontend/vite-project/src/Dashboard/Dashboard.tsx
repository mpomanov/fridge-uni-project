import { useState, useEffect } from "react";
import CameraCard from "./Cameracard";

interface Camera {
  id: number;
  compressor_on: boolean;
  ventilation_on: boolean;
  heater_on: boolean;
  auto_mode: boolean;
  target_temperature: number | null;
  defrost_threshold_temperature: number | null;
  temperature: number | null;
  evaporator_temperature: number | null;
  supply_voltage: number | null;
  status: string | null;
  problem: boolean;
}

interface DashboardProps {
  fetchData: (endpoint: string, options?: RequestInit, setLoading?: React.Dispatch<React.SetStateAction<boolean>>) => Promise<Response | null>;
}

export default function Dashboard({ fetchData }: DashboardProps) {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [logoutLoading, setLogoutLoading] = useState<boolean>(false);

  const loadCameras = async () => {
    const res = await fetchData("/dashboard");
    if (!res) return;
    const data = await res.json();
    setCameras(data);
    setLoading(false);
  };


  const handleLogout = async () => {
    try{
      setLogoutLoading(true)
      await fetchData("/logout", { method: "POST" });
      window.location.href = "/login";
    } catch(error: any) {
      console.error(error)
    } finally {
      setLogoutLoading(false)
    }
  };

  useEffect(() => {
    loadCameras();
    const interval = setInterval(loadCameras, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-white font-sans relative">
      <div className="fixed top-[-200px] right-[-200px] w-[500px] h-[500px] rounded-full bg-[#ff7828] opacity-5 pointer-events-none" />

      <div className="relative z-10 p-4 md:p-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8 pb-6 border-b border-black/5">
          <div>
            <h1 className="text-2xl font-bold text-black tracking-tight">ХладоСтраж</h1>
            <p className="text-xs text-black/30 mt-0.5">Система за Мониторинг и Контрол</p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-black/5 rounded-full px-4 py-2">
              <div className="w-2 h-2 rounded-full bg-[#ff7828] shadow-[0_0_8px_#ff7828] animate-pulse" />
              <span className="text-black/50 text-xs">Включен</span>
            </div>
            <span className="hidden md:block text-xs text-black/30">
              {new Date().toLocaleDateString()} · {new Date().toLocaleTimeString()}
            </span>
            <button
              onClick={handleLogout}
              disabled={logoutLoading}
              className={`bg-black/5 hover:bg-black/10 text-black/50 text-xs px-4 py-2 rounded-full transition-colors ${logoutLoading ? "opacity-50" : ""} cursor-pointer`}
            >
              {logoutLoading ? "Излиза се..." : "Изход"}
            </button>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center h-64 text-black/30 text-sm">
            Зарежда обекти...
          </div>
        ) : cameras.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-black/30 text-sm">
            Няма налични обекти
          </div>
        ) : (
          <>
            <div
              className="flex md:hidden gap-4 overflow-x-auto pb-4 snap-x snap-mandatory"
              style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
            >
              {cameras.map((camera) => (
                <div key={camera.id} className="snap-center flex-shrink-0 w-[85vw]">
                  <CameraCard camera={camera} fetchData={fetchData} />
                </div>
              ))}
            </div>
            <div className="hidden md:grid grid-cols-2 xl:grid-cols-4 gap-4">
              {cameras.map((camera) => (
                <CameraCard key={camera.id} camera={camera} fetchData={fetchData} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}