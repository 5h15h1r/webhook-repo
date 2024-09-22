'use client'
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const App = () => {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await axios.get('https://webhook-repo-dnop.onrender.com/webhook/events');
        setEvents(response.data);
        console.log(response.data);
      } catch (error) {
        console.error('Error fetching events', error);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-5">
      <div className="bg-white shadow-md rounded-lg p-6 max-w-4xl w-full">
        <h1 className="text-2xl font-bold text-gray-800 mb-4 text-center">Action Repo Events</h1>
        <ul className="space-y-4">
          {events.map(event => (
            <li key={event._id} className="p-4 bg-gray-50 border border-gray-200 rounded-md">
              {event.action === 'push' && (
                <span className="text-gray-700 font-medium">
                  {event.author} pushed to <span className="font-bold">{event.to_branch}</span> on{' '}
                  <span className="text-gray-500">{new Date(event.timestamp).toLocaleString()}</span>
                </span>
              )}
              {event.action === 'pull' && (
                <span className="text-gray-700 font-medium">
                  {event.author} submitted a pull request from <span className="font-bold">{event.from_branch}</span> to{' '}
                  <span className="font-bold">{event.to_branch}</span> on{' '}
                  <span className="text-gray-500">{new Date(event.timestamp).toLocaleString()}</span>
                </span>
              )}
              {event.action === 'merge' && (
                <span className="text-gray-700 font-medium">
                  {event.author} merged branch <span className="font-bold">{event.from_branch}</span> to{' '}
                  <span className="font-bold">{event.to_branch}</span> on{' '}
                  <span className="text-gray-500">{new Date(event.timestamp).toLocaleString()}</span>
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;
