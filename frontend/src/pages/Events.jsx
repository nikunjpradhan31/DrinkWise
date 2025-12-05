// import React, { useState, useEffect } from "react";
// import { useEventsContext } from "../context/EventsContext";
// import { useAuthContext } from "../context/AuthContext";
// import {
//   Container,
//   Row,
//   Col,
//   Button,
//   Form,
//   Spinner,
//   Alert,
//   Modal,
//   Card,
//   ListGroup,
// } from "react-bootstrap";
// import { useMovieContext } from "../context/MovieContext";
// import WatchListView from "../components/ViewWatchList";


// const EventsPage = () => {
//   const { user } = useAuthContext();

//   const {
//     events,
//     Invitedevents,
//     fetchUserEvents,
//     fetchInvitedEvents,
//     createEvent,
//     updateEvent,
//     deleteEvent,
//     eventError,
//     isLoading,
//     fetchPublicEvents,
//     PublicEvents,
//     addInvitee,
//     PublicError,
//     isPublicLoading,
//   } = useEventsContext();
//   const { fetchUserWatchlists, watchlists, fetchSingleWatchList, singlewatchlists } = useMovieContext();

//   const [publicwatchlists, setpublicwatchlists] = useState(null);

//   useEffect(() => {
//     if (user) {
//       fetchUserEvents(user.user_id, user.access_token);
//       fetchInvitedEvents(user.user_id,user.access_token);
//       fetchUserWatchlists();

//     }
//   }, [user, fetchUserEvents, fetchInvitedEvents, fetchUserWatchlists,setpublicwatchlists]);

//   useEffect(() => {
//     if (watchlists) {
//       setpublicwatchlists(watchlists.filter((watchlist) => !watchlist.is_private));
//     }
//   }, [watchlists]);

//   const [showModal, setShowModal] = useState(false);
//   const [modalType, setModalType] = useState("create");
//   const [eventData, setEventData] = useState({
//     event_name: "",
//     event_time: "",
//     event_location: "",
//     description: "",
//     watchlist_id: undefined,
//     is_public: false,
//     event_creator: 0,
//     access_token : user?.access_token || "",
//   });
//   const [selectedEventId, setSelectedEventId] = useState(null);

//   const handleModalShow = (type, event) => {
//     setModalType(type);
//     if (type === "edit" && event) {
//       setEventData(event);
//       setSelectedEventId(event.event_id || null);
//     } else {
//       setEventData({
//         event_name: "",
//         event_time: "",
//         event_location: "",
//         description: "",
//         watchlist_id: undefined,
//         is_public: false,
//         event_creator: user?.user_id || 0,
//         access_token: user?.access_token || "",
//       });
//     }
//     setShowModal(true);
//   };

//   const handleModalClose = () => {
//     setShowModal(false);
//     setSelectedEventId(null);
//   };
//   const handleEventSubmit = async () => {
//     try {
//       if (modalType === "create") {
//         await createEvent(eventData);
//       } else if (selectedEventId) {
        
//         await updateEvent({ ...eventData, event_id: selectedEventId, event_creator_name: user.username, access_token: user.access_token });
//       }
//       handleModalClose();
//     } catch (error) {
//       console.error("Failed to create or update event", error);
//     }
//   };

//   const handleDeleteEvent = async (eventId, access_token) => {
//     try {
//       await deleteEvent(eventId, access_token);
//     } catch (error) {
//       console.error("Failed to delete event", error);
//     }
//   };

//   const handleWatchlistSelection = (watchlistId) => {
//     if (watchlistId) {
//     setEventData((prev) => ({
//       ...prev,
//       watchlist_id: watchlistId,
//     }));
//   }
//   };

//   const [showModalWatchlist, setShowModalWatchlist] = useState(false);


//   const handleShowModalWatchList = () => {
//     if (singlewatchlists) {
//       setShowModalWatchlist(true);

//     }
//   };
//   const handleCloseModalWatchList = () => {
//     setShowModalWatchlist(false);
//   };
  
//   const [searchString, setSearchString] = useState("");
//   const [searchResults, setSearchResults] = useState(null);

//   const handleSearch = async () => {
//     if (user && searchString.trim() !== "") {
//       await fetchPublicEvents(user.user_id, searchString);
//       setSearchResults(PublicEvents);
//     }
//   };

//   const handleSelectEvent = async (event) => {
//     try {
//       if (user) {
//         await addInvitee({ event_id: event.event_id, invitee: user.user_id, access_token: user.access_token });
//         setSearchString("");
//         setSearchResults(null);
//         fetchInvitedEvents(user.user_id);
//       }
//     } catch (error) {
//       console.error("Failed to add invitee:", error);
//     }
//   };

//   const handleClearSearch = () => {
//     setSearchString("");
//     setSearchResults(null);
//   };

//   return (
//     <Container className="mt-4">
//       <div className="d-flex justify-content-between align-items-center">
//         <h2>Events</h2>
//         <Button variant="primary" onClick={() => handleModalShow("create")}>
//           + Create Event
//         </Button>
//       </div>
//       {isLoading && <Spinner animation="border" />}

//       {/* User's Created Events */}
//       <h3 className="mt-4">Your Created Events</h3>
//       {events && events.length > 0 ? (
//         <Row>
//           {events.map((event) => (
//             <Col md={6} lg={4} className="mb-4" key={event.event_id}>
//               <Card>
//                 <Card.Body>
//                   <Card.Title>{event.event_name}</Card.Title>
//                   <Card.Text>{event.description}</Card.Text>
//                   <Card.Text>
//                     <strong>Location:</strong> {event.event_location}
//                   </Card.Text>
//                   <Card.Text>
//                     <strong>Time:</strong>{" "}
//                     {new Date(event.event_time).toLocaleString()}
//                   </Card.Text>
//                   <Card.Text>
//                     <strong>Watchlist:</strong>{" "}
//                     {event.watchlist_id === null ? (
//                       "None"
//                     ) : (
//                       <Button
//                         variant="link"
//                         onClick={() => {
//                           if(event.watchlist_id)
//                             fetchSingleWatchList(event.watchlist_id);
//                           handleShowModalWatchList()
//                         }}
//                       >
//                         View Watchlist
//                       </Button>
//                     )}

//                     <WatchListView
//                       show={showModalWatchlist}
//                       onHide={handleCloseModalWatchList}
//                       watchlistDetails={singlewatchlists} // Pass singleWatchlist as details
//                       isGuest={true} // Pass the isGuest prop
//                     />
//                     </Card.Text>
//                   <Button
//                     variant="warning"
//                     onClick={() => handleModalShow("edit", event)}
//                   >
//                     Edit
//                   </Button>{" "}
//                   <Button
//                     variant="danger"
//                     onClick={() => handleDeleteEvent(event.event_id, user.access_token)}
//                   >
//                     Delete
//                   </Button>
//                 </Card.Body>
//               </Card>
//             </Col>
//           ))}
//         </Row>
//       ) : (
//         <Alert variant="info">You haven't created any events yet.</Alert>
//       )}

// <Form className="my-4">
//         <Form.Group controlId="searchPublicEvents">
//           <Form.Label>Search Public Events</Form.Label>
//           <div className="d-flex">
//             <Form.Control
//               type="text"
//               placeholder="Enter event name"
//               value={searchString}
//               onChange={(e) => setSearchString(e.target.value)}
//             />
//             <Button variant="primary" className="ms-2" onClick={handleSearch}>
//               Search
//             </Button>
//             <Button variant="secondary" className="ms-2" onClick={handleClearSearch}>
//               Clear
//             </Button>
//           </div>
//         </Form.Group>
//       </Form>

//       {/* Search Results */}
//       {isPublicLoading && <Spinner animation="border" />}
//       {PublicError && <Alert variant="danger">{PublicError}</Alert>}
//       {searchResults && searchResults.length > 0 ? (
//         <ListGroup className="mb-4">
//           {searchResults.map((event) => (
//             <ListGroup.Item
//               key={event.event_id}
//               action
//               onClick={() => handleSelectEvent(event)}
//             >
//               {event.event_name} - Created by {event.event_creator_name}
//             </ListGroup.Item>
//           ))}
//         </ListGroup>
//       ) : (
//         searchString &&
//         !isPublicLoading &&
//         !PublicError && <Alert variant="info">No events found.</Alert>
//       )}

//       {/* Invited Events */}
//       <h3 className="mt-4">Events You’re Invited To</h3>
//       {Invitedevents && Invitedevents.length > 0 ? (
//         <Row>
//           {Invitedevents.map((event) => (
//             <Col md={6} lg={4} className="mb-4" key={event.event_id}>
//               <Card>
//                 <Card.Body>
//                   <Card.Title>{event.event_name}</Card.Title>
//                   <Card.Text>{event.description}</Card.Text>
//                   <Card.Text>
//                     <strong>Location:</strong> {event.event_location}
//                   </Card.Text>
//                   <Card.Text>
//                     <strong>Time:</strong>{" "}
//                     {new Date(event.event_time).toLocaleString()}
//                   </Card.Text>
//                   <Card.Text>
//                     <strong>Watchlist:</strong>{" "}
//                     {event.watchlist_id === null ? (
//                       "None"
//                     ) : (
//                       <Button
//                         variant="link"
//                         onClick={() => {
//                           if(event.watchlist_id)
//                             fetchSingleWatchList(event.watchlist_id);
//                           handleShowModalWatchList()
//                         }}
//                       >
//                         View Watchlist
//                       </Button>
//                     )}

//                     <WatchListView
//                       show={showModalWatchlist}
//                       onHide={handleCloseModalWatchList}
//                       watchlistDetails={singlewatchlists} // Pass singleWatchlist as details
//                       isGuest={true} // Pass the isGuest prop
//                     />
//                     </Card.Text>
//                 </Card.Body>
//               </Card>
//             </Col>
//           ))}
//         </Row>
//       ) : (
//         <Alert variant="info">You’re not invited to any events yet.</Alert>
//       )}

//       {/* Create/Edit Event Modal */}
//       <Modal show={showModal} onHide={handleModalClose} centered>
//         <Modal.Header closeButton>
//           <Modal.Title>
//             {modalType === "create" ? "Create Event" : "Edit Event"}
//           </Modal.Title>
//         </Modal.Header>
//         <Modal.Body>
//           <Form>
//             <Form.Group>
//               <Form.Label>Event Name</Form.Label>
//               <Form.Control
//                 type="text"
//                 value={eventData.event_name}
//                 onChange={(e) =>
//                   setEventData((prev) => ({
//                     ...prev,
//                     event_name: e.target.value,
//                   }))
//                 }
//               />
//             </Form.Group>
//             <Form.Group>
//               <Form.Label>Event Time</Form.Label>
//               <Form.Control
//                 type="datetime-local"
//                 value={eventData.event_time}
//                 onChange={(e) =>
//                   setEventData((prev) => ({
//                     ...prev,
//                     event_time: e.target.value,
//                   }))
//                 }
//               />
//             </Form.Group>
//             <Form.Group>
//               <Form.Label>Location</Form.Label>
//               <Form.Control
//                 type="text"
//                 value={eventData.event_location}
//                 onChange={(e) =>
//                   setEventData((prev) => ({
//                     ...prev,
//                     event_location: e.target.value,
//                   }))
//                 }
//               />
//             </Form.Group>
//             <Form.Group>
//               <Form.Label>Description</Form.Label>
//               <Form.Control
//                 as="textarea"
//                 rows={3}
//                 value={eventData.description}
//                 onChange={(e) =>
//                   setEventData((prev) => ({
//                     ...prev,
//                     description: e.target.value,
//                   }))
//                 }
//               />
//             </Form.Group>

//     {publicwatchlists && publicwatchlists.length > 0 ? (
//       <Form.Group>
//   <Form.Label>Select Watchlist</Form.Label>
//   <ListGroup>
//     <ListGroup.Item
//       active={eventData.watchlist_id === null} // Check for null
//       onClick={() => handleWatchlistSelection(null)} // Set to null
//     >
//       None
//     </ListGroup.Item>
//     {publicwatchlists.map((watchlist) => (
//       <ListGroup.Item
//         key={watchlist.watchlist_id}
//         active={eventData.watchlist_id === watchlist.watchlist_id}
//         onClick={() => handleWatchlistSelection(watchlist.watchlist_id)}
//       >
//         {watchlist.watchlist_title}
//       </ListGroup.Item>
//     ))}
//   </ListGroup>
// </Form.Group>

// ) : (
//   <Alert variant="info">No public watchlists available.</Alert>
// )}
// <Form.Group>
//   <Form.Check
//     type="checkbox"
//     label="Public Event"
//     checked={eventData.is_public}
//     onChange={(e) =>
//       setEventData((prev) => ({
//         ...prev,
//         is_public: e.target.checked,
//       }))
//     }
//   />
// </Form.Group>

//           </Form>
//         </Modal.Body>
//         <Modal.Footer>
//           <Button variant="secondary" onClick={handleModalClose}>
//             Cancel
//           </Button>
//           <Button variant="primary" onClick={handleEventSubmit}>
//             {modalType === "create" ? "Create" : "Save Changes"}
//           </Button>
//         </Modal.Footer>
//       </Modal>

//       {eventError && <Alert variant="danger">{eventError}</Alert>}
//     </Container>
//   );
// };

// export default EventsPage;
