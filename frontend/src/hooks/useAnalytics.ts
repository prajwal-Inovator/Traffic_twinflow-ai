import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

export function useDashboardMetrics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiClient.get("/analytics");
        setData(res.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, []);

  return data;
}