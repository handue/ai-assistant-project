const API_URL =
    process.env.NEXT_PUBLIC_API_URL;

export async function apiGet<T>(path: string): Promise<T> {

    // if (!API_URL) {
    //     console.log("API_URL is not defined");
    //     throw new Error("API_URL is not defined");
    // }

    const response = await fetch(`${API_URL}${path}`);



    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
}

export async function apiPost<TRequest, TResponse>(path: string, body: TRequest): Promise<TResponse> {
    const response = await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    return response.json();
}