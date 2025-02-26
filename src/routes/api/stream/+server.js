export async function GET({ url }) {
    const target = new URL('http://127.0.0.1:5000/stream');
    const response = await fetch(target);
    
    return new Response(response.body, {
        headers: {
            'Content-Type': response.headers.get('Content-Type'),
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
    });
}
