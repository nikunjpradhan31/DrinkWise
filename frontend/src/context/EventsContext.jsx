import React, { createContext, useContext, useState, ReactNode, useCallback } from "react";
import { axiosInstance } from "../utils/axiosHelper";
import { useAuthContext } from "./AuthContext";


// Create context
const EventsContext = createContext(undefined);


export const EventsContextProvider = ({ children }) => {
  const {user} = useAuthContext()
  const [events, setEvents] = useState(null);
  const [eventError, setEventError] = useState(null);
  const [Invitedevents, setInvitedEvents] = useState(null);
  const [InvitedeventError, setInvitedEventError] = useState(null);
  const [isInvitedLoading, setIsInvitedLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [PublicError, setPublicError] = useState(null);
  const [isPublicLoading, setisPublicLoading] = useState(false);
  const [PublicEvents,setPublicEvents] = useState(null);
  const [InviteeError, setInviteeError] = useState(null);


  const fetchUserEvents = useCallback(async (username,access_token) => {
    setIsLoading(true);
    setEventError(null);
    try {
      const response = await axiosInstance.get(`/event/users/${username}/${access_token}`);
      setEvents(response.data.events);
    } catch (error) {
      setEventError(error.response?.data?.detail || "Failed to fetch user events.");
    } finally {
      setIsLoading(false);
    }
  }, []);
  const fetchInvitedEvents = useCallback(async (username,access_token) => {
    setIsInvitedLoading(true);
    setInvitedEventError(null);
    try {
      const response = await axiosInstance.get(`/event/invited/${username}/${access_token}`);
      setInvitedEvents(response.data.events);
    } catch (error) {
      setInvitedEventError(error.response?.data?.detail || "Failed to fetch invited events.");
    } finally {
      setIsInvitedLoading(false);
    }
  }, []);

  const fetchPublicEvents = useCallback(async (username, substring) => {
    setisPublicLoading(true);
    setPublicError(null);
    try {
      const response = await axiosInstance.get(`/event/public/${username}/${substring}`);
      setPublicEvents(response.data.events);
    } catch (error) {
      setPublicError(error.response?.data?.detail || "Failed to fetch public events.");
    } finally {
      setisPublicLoading(false);
    }
  }, []);

  const createEvent = useCallback(async (data) => {
    setEventError(null);
    try {
      await axiosInstance.post(`/event/create`, data);
      if(user?.user_id)
        fetchUserEvents(user?.user_id,user?.access_token);
    } catch (error ) {
      setEventError(error.response?.data?.detail || "Failed to create event.");
    }
  }, [fetchUserEvents,user]);

  const updateEvent = useCallback(async (data) => {
    setEventError(null);
    try {
      await axiosInstance.put(`/event/update/`, data);
      if(user?.username)
        fetchUserEvents(user?.user_id, user?.access_token);
    } catch (error) {
      setEventError(error.response?.data?.detail || "Failed to update event.");
    }
  }, [fetchUserEvents,user]);

  const deleteEvent = useCallback(async (eventId, access_token) => {
    setEventError(null);
    try {
      await axiosInstance.delete(`/event/delete/${eventId}/${access_token}`);
      if(user?.username)
        fetchUserEvents(user?.user_id,user?.access_token);
    } catch (error) {
      setEventError(error.response?.data?.detail || "Failed to delete event.");
    }
  }, [fetchUserEvents,user]);

  const addInvitee = useCallback(async (data) => {
    setInviteeError(null);
    try {
      await axiosInstance.post(`/event/add_invitee`, data);
    } catch (error) {
      setInviteeError(error.response?.data?.detail || "Failed to add invitee.");
    }
  }, []);

  const fetchInvitedUsers = useCallback(async (eventId) => {
    setEventError(null);
    try {
      const response = await axiosInstance.get(`/event/invited_users/${eventId}`);
      return response.data;
    } catch (error) {
      setEventError(error.response?.data?.detail || "Failed to fetch invited users.");
      return [];
    }
  }, []);

  return (
    <EventsContext.Provider
      value={{
        events,
        fetchUserEvents,
        fetchInvitedEvents,
        //fetchPublicEvents,
        createEvent,
        updateEvent,
        deleteEvent,
        addInvitee,
        fetchInvitedUsers,
        eventError,
        isLoading,
        InvitedeventError,
        Invitedevents,
        isInvitedLoading,
        PublicError,
        PublicEvents,
        isPublicLoading,
        fetchPublicEvents,
        InviteeError,
      }}
    >
      {children}
    </EventsContext.Provider>
  );
};

export const useEventsContext = () => {
  const context = useContext(EventsContext);
  if (!context) {
    throw new Error("useEventsContext must be used within an EventsContextProvider");
  }
  return context;
};
