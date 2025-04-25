import React, { useState } from 'react'

const Accordion = ({ title, data }) => {
  const [accordionOpen, setAccordionOpen] = useState(false);

  return (
    <div className={`accordion ${accordionOpen ? 'expanded' : ''}`}>
      <button className='accordion-button'
        onClick={() => setAccordionOpen(!accordionOpen)}
      >
        <div className="plus-minus">
          {accordionOpen ? <h3>-</h3> : <h3>+</h3>}
        </div>
        <h3>{title}</h3>
      </button>
      <div className='accordion-list'>
        {data}
      </div>
    </div>
  )
}

export default Accordion