import { useEffect, useState } from "react";
import api from "../api/client";

export default function useAnalytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get("/analytics");
        setData(res.data);
        console.log(res.data);
      } catch (err) {
        console.error("Analytics error:", err);
      }
    };

    fetchData();
  }, []);

  return data;
}