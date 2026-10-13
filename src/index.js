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
        const targetUrl = new URL(decodedUrl);

        // Preparamos los headers que mandará el Worker hacia el stream original
        const newHeaders = new Headers(request.headers);

        // Opcional: Si el servidor de streaming exige un Referer o User-Agent específico, podés definirlo acá:
        // newHeaders.set('Referer', 'https://tu-sitio-web.com');
        // newHeaders.set('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');

        // Realizamos el fetch como proxy transparente
        const response = await fetch(targetUrl.toString(), {
          method: request.method,
          headers: newHeaders,
          body: request.body,
          redirect: 'follow'
        });

        // Devolvemos la respuesta manteniendo los headers y cors del stream original
        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers
        });

      } catch (err) {
        return new Response('Error al procesar la URL o formato Base64 inválido.', { status: 400 });
      }
    }

    // Ruta por defecto
    return new Response('Proxy M3U8 Activo. Usá /play?u=BASE64', { status: 200 });
  },
};
