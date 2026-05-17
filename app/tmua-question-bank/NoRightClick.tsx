"use client";
import { useEffect } from "react"; export default function NoRightClick() { useEffect(() => { const handler = (e: MouseEvent) => { e.preventDefault(); }; document.addEventListener("contextmenu", handler, true); return () => document.removeEventListener("contextmenu", handler, true); }, []); return null;
}