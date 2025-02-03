import { useState } from "react"
import { useRouter } from "next/router";
import LogOut from "../components/LogOut"
export default function Menu() {
    const router = useRouter();

    return (
        <div>
            <div> tutaj będzie menu </div>
            <LogOut router={router}/>
        </div>

    )
}