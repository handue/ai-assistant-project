"use client";

import {
    QueryClient,
    QueryClientProvider,
} from "@tanstack/react-query";
import { useState } from "react";

export default function Providers({
    children,
}: {
    children: React.ReactNode;
}) {
    const [queryClient] = useState(
        () => new QueryClient()
    );

    // keep QUeryClient even if Providers component is re-rendered

    //   make all of client components have access to react-query's QueryClientProvider, 
    // which allows them to use react-query hooks like useQuery and useMutation. This is necessary for managing server state in a React application.

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}