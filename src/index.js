export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Verificamos si la ruta es /play
    if (url.pathname === '/play') {
      const base64Param = url.searchParams.get('u');

      if (!base64Param) {
        return new Response('Falta el parámetro ?u= (Base64)', { status: 400 });
      }

      try {
        // Decodificamos de Base64 a texto plano
        const decodedUrl = atob(base64Param);

        // Validamos que sea una URL válida
        const targetUrl = new URL(decodedUrl);


        
        // Proxy real: mantiene la URL del proxy en el navegador
        const response = await fetch(targetUrl.toString(), {
          method: request.method,
          headers: request.headers,
          redirect: "follow"
        });

        // Devolver la respuesta sin redireccionar al navegador
        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers
        });
        

      } catch (err) {
        return new Response('El formato Base64 es inválido o la URL está corrupta.', { status: 400 });
      }
    }

    // Ruta por defecto si entran a la raíz del Worker
    return new Response('ZIPTV Proxy activo. Usá /play?u=BASE64', { status: 200 });
  },
};
