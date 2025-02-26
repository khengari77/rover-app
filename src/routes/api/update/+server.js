// In your server's routes (e.g., /api/update)
export async function GET({ url }) {
    const target = new URL('http://192.168.4.100/update');
    try {
        // For GET, fetch the full response (including body)
        const response = await fetch(target);
        return new Response(await response.text(), {
            headers: {
                'Content-Type': response.headers.get('Content-Type') || 'application/json'
            }
        });
    } catch (err) {
        return new Response('External server error', { status: 502 });
    }
}

export async function HEAD({ url }) {
    const target = new URL('http://192.168.4.100/update');
    try {
        // For HEAD, only check headers (no body)
        const response = await fetch(target, { method: 'HEAD', timeout: 3000 });
        if (response.ok) {
            return new Response(null, { status: 200 }); // No body needed
        }
        return new Response(null, { status: response.status });
    } catch (err) {
        return new Response(null, { status: 502 });
    }
}
