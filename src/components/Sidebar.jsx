import React, { useState } from 'react'
import Accordion from './Accordion'
import villagers from '../villagers.json'

import School from '../assets/images/SchoolIcon.png'
import Cafe from '../assets/images/CafeIcon.png'
import Restaurant from '../assets/images/RestaurantIcon.png'
import Hospital from '../assets/images/HospitalIcon.png'
import ApparelShop from '../assets/images/ApparelShopIcon.png'
import Leif from '../assets/images/Leif.png'

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const toggle = () => setIsOpen(!isOpen);

  return (
    <div className="sidebar">
      <button className="sidebar-toggle" onClick={toggle}>
        <svg width="32px" height="32px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 18L20 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 12L20 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M4 6L20 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>

      <div className={`checklist ${isOpen ? 'open' : ''}`}>
        <h2>Checklist</h2>

        <div className="villagers">
          <Accordion
            title="Villagers"
            data={villagers.map((villager) => (
              <div className="accordion-item">
                <img src={villager.Image} alt="Villager image" />
                <h4>{villager.Name}</h4>
              </div>
            ))}
          />
        </div>

        <div className="facilities">
          <Accordion
            title="Facilities & Milestones"
            data={
              <>
              <div className="accordion-item">
                <img src={School} alt="School image" />
                <h4>School</h4>
              </div>
              <div className="accordion-item">
                <img src={Cafe} alt="Cafe image" />
                <h4>Cafe</h4>
              </div>
              <div className="accordion-item">
                <img src={Restaurant} alt="Restaurant image" />
                <h4>Restaurant</h4>
              </div>
              <div className="accordion-item">
                <img src={Hospital} alt="Hospital image" />
                <h4>Hospital</h4>
              </div>
              <div className="accordion-item">
                <img src={ApparelShop} alt="Apparel shop image" />
                <h4>Apparel Shop</h4>
              </div>
              <div className="accordion-item">
                <img src={Leif} alt="Leif image" />
                <h4>Leif Lesson</h4>
              </div>
              </>
            }
          />
        </div>

        <button className="checklist-button">
          Placeholder button
        </button>
      </div>
    </div>
  )
}

export default Sidebar
