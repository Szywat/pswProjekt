"use client";
import { io } from "socket.io-client"

const socket = io("ws://127.0.0.1:5000");
export default function Chat() {


    return (
        <div id="chatbox"> 
            <ul id="messages">
            </ul>    
                <form id="form" action="">
                    <input id="input" autoComplete="off"></input><button>Send</button>
                </form>
            
        </div>
       
    )
}