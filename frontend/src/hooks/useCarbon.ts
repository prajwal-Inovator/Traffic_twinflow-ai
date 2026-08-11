import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

export function useCarbonDashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiClient.get("/carbon");
        setData(res.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, []);

  return data;
}