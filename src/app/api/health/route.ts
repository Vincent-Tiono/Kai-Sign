export async function GET() {
  return new Response(
    JSON.stringify({ status: "ok", message: "Next.js API is running" }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
} 