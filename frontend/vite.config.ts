import { defineConfig } from "vite";
import dns from "dns";
import react from "@vitejs/plugin-react";

dns.setDefaultResultOrder("verbatim");

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "localhost",
    port: 3000,
    proxy: {
      '/cypher-talk': {
        target: 'https://20.96.176.239',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/cypher-talk/, '/cypher-talk'),
      },
    },
    // headers: {
    //   'Access-Control-Allow-Credentials': 'true',
    //   'Access-Control-Allow-Origin': '*',
    //   'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
    //   'Access-Control-Allow-Headers': 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version',
    // }
  }
});
