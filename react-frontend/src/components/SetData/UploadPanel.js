import React from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import UploadForm from './UploadForm'

export default function UploadPanel() {
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>
            <UploadForm / >
        </div>
    )
}
