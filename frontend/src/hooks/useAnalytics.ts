import { useEffect, useState } from "react";
import { apiClient } from "../api/client";

export function useDashboardMetrics() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiClient.get("/analytics");
        setData(res.data);
      } catch (err) {
        setIsError(true);
        setError(err);
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, isLoading, isError, error };
}