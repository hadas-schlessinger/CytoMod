import React from 'react'
import transperantBackground from '../../transperantBackground.png'
import UploadForm from './UploadForm'

export default function UploadPanel() {
    return (
        <div style={{backgroundImage: `url(${transperantBackground})`}}>
            <UploadForm / >
        </div>
    )
}
