import { useEffect, useState } from "react";
import api from "../api/client";

export default function useCarbon() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get("/carbon");
        setData(res.data);
        console.log(res.data);
      } catch (err) {
        console.error("Carbon error:", err);
      }
    };

    fetchData();
  }, []);

  return data;
}