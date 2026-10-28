import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

const target=process.env.SAMANVAY_API_TARGET??'http://127.0.0.1:8000';
if(!/^http:\/\/127\.0\.0\.1:\d+$/.test(target))throw new Error('The synthetic prototype proxy must use an explicit loopback port.');
export default defineConfig({plugins:[react()],server:{proxy:{'/api':target},fs:{strict:true,
  allow:[fileURLToPath(new URL('.',import.meta.url))],deny:['.env','.env.*','**/.local-data/**','**/.demo-contexts/**','**/backend/**']}},preview:{proxy:{'/api':target}}});
