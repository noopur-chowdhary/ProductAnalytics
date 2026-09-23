const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000";

export async function fetchJson(path: string) {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(
      `${path}: HTTP ${response.status}`
    );
  }

  return response.json();
}

export async function getDashboardData() {
  const endpoints = {
    health: "/health",
    overview: "/api/overview",

    retailrocketAnalytics:
      "/api/analytics/retailrocket",

    onlineRetail:
      "/api/analytics/online-retail",

    experiment:
      "/api/analytics/experiment",

    retailrocketPropensity:
      "/api/propensity/retailrocket",

    criteoUplift:
      "/api/uplift/criteo",

    decisions:
      "/api/decisions",
  };

  const entries = await Promise.all(
    Object.entries(endpoints).map(
      async ([key, path]) => {
        try {
          const value = await fetchJson(path);

          return [
            key,
            value,
            null,
          ] as const;
        } catch (error) {
          return [
            key,
            null,
            error instanceof Error
              ? error.message
              : "Request failed",
          ] as const;
        }
      }
    )
  );

  const data: Record<string, any> = {};
  const errors: string[] = [];

  for (const [key, value, error] of entries) {
    data[key] = value;

    if (error) {
      errors.push(error);
    }
  }

  return {
    ...data,
    errors,
  };
}
