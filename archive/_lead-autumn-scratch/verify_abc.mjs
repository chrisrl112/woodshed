#!/usr/bin/env node
/* verify_abc.mjs <input.abc> <output.png>
   Renders ABC notation to PNG via abcjs+jsdom so the transcriber can visually
   diff their transcription against the source image. Requires: npm i jsdom abcjs ; ImageMagick `convert`. */
import {JSDOM} from 'jsdom';
import {execSync} from 'child_process';
import fs from 'fs';
const [,,inFile,outPng]=process.argv;
if(!inFile||!outPng){console.error('usage: verify_abc.mjs in.abc out.png');process.exit(1);}
const abc=fs.readFileSync(inFile,'utf8');
const dom=new JSDOM('<div id="x"></div>',{pretendToBeVisual:true});
global.window=dom.window; global.document=dom.window.document;
const ABCJS=(await import('abcjs')).default;
ABCJS.renderAbc(dom.window.document.getElementById('x'),abc,{staffwidth:1100,scale:1.4,paddingtop:14,paddingbottom:24});
const svg=dom.window.document.querySelector('svg');
if(!svg){console.error('RENDER FAILED — ABC has syntax errors');process.exit(2);}
svg.setAttribute('xmlns','http://www.w3.org/2000/svg');
const tmp=outPng+'.svg';
fs.writeFileSync(tmp,'<?xml version="1.0"?>'+svg.outerHTML.replace(/currentColor/g,'#000'));
execSync(`convert -density 110 -background white ${JSON.stringify(tmp)} ${JSON.stringify(outPng)}`);
try{fs.unlinkSync(tmp);}catch(e){}
console.log('OK rendered',outPng);
