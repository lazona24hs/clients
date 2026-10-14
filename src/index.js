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


     
        // Opción A: Redirección directa (302) al enlace original
        return Response.redirect(targetUrl.toString(), 302);
 
         
        //  Nota: Si preferís que el Worker haga de proxy real (pasando el tráfico por Cloudflare 
         // en lugar de redirigir), podés descomentar el siguiente bloque y comentar la línea de arriba:
         /* 
          return fetch(targetUrl.toString(), {
            headers: request.headers
          });
         */

      } catch (err) {
        return new Response('El formato Base64 es inválido o la URL está corrupta.', { status: 400 });
      }
    }

    // Ruta por defecto si entran a la raíz del Worker
    return new Response('ZIPTV Proxy activo. Usá /play?u=BASE64', { status: 200 });
  },
};
