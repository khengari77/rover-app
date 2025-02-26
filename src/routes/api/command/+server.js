export async function POST({ request }) {
    try {
        const roverEndpoint = 'http://192.168.4.100/command';
        const body = await request.json();
        
        const response = await fetch(roverEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Add any required authentication headers
            },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            return new Response(await response.text(), {
                status: response.status,
                headers: {
                    'Content-Type': 'text/plain'
                }
            });
        }

        return new Response(JSON.stringify(await response.json()), {
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (err) {
        return new Response(JSON.stringify({
            error: 'Internal server error'
        }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
}
