"use client";

import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../lib/api";


type BackendHealth = {
    status: string;
};

export default function BackendStatus() {
    const { data, isPending, error } = useQuery({
        queryKey: ["backend-health"],

        queryFn: () => apiGet<BackendHealth>("/health"),


    });

    if (isPending) {
        return <p>Checking backend...</p>;
    }

    if (error) {
        return <p>Backend disconnected</p>;
    }

    return <p>Backend status: {data.status}</p>;
}