export async function GET({ url }) {
    const target = new URL('http://192.168.4.100/update');
    const response = await fetch(target);
    return new Response(await response.text(), {
        headers: {
            'Content-Type': 'application/json'
        }
    });
}
