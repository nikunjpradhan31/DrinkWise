import React, { useEffect, useState } from "react";
import { Modal, Button, Card, ListGroup, Image, Col } from "react-bootstrap";
import { useMovieContext } from "../context/MovieContext";
import { useNavigate } from "react-router-dom";

const WatchListView = ({
  show,
  onHide,
  watchlistDetails,
  isGuest = false, // Default to false if not provided
}) => {
  const navigate = useNavigate();
  const [movies, setMovies] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { getMoviesInWatchlist } = useMovieContext();

  useEffect(() => {
    
    const fetchMovies = async () => {
      try {
        setIsLoading(true);
        const fetchedMovies = await getMoviesInWatchlist(
          watchlistDetails?.watchlist_id || 0
        );
        setMovies(fetchedMovies);
      } catch (err) {
        setError("Failed to fetch movies in the watchlist. Please try again.");
      } finally {
        setIsLoading(false);
      }
    };

    if (watchlistDetails) {
      fetchMovies();
    }
  }, [getMoviesInWatchlist, watchlistDetails]);

  if (!watchlistDetails) {
    return null;
  }

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>{watchlistDetails.watchlist_title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Col>
          <p>
            <strong>Privacy:</strong>{" "}
            {watchlistDetails.is_private ? "Private" : "Public"}
          </p>
          <p>
            <strong>Created At:</strong>{" "}
            {new Date(watchlistDetails.created_at).toLocaleDateString()}
          </p>
          <p>
            <strong>Movies:</strong> {watchlistDetails.number_of_movies}
          </p>
        </Col>

        {watchlistDetails.number_of_movies !== 0 ? (
          <Card>
            <Card.Header as="h3">Movies in Watchlist</Card.Header>
            <ListGroup variant="flush">
              {movies.map((movie) => (
                <ListGroup.Item key={movie.movie_id}>
                  <div className="d-flex align-items-center justify-content-between">
                    {/* Movie Image and Details */}
                    <div className="d-flex align-items-center">
                      <Image
                        src={movie.image_url}
                        alt={movie.title}
                        rounded
                        style={{
                          width: "80px",
                          height: "120px",
                          objectFit: "cover",
                          marginRight: "15px",
                        }}
                      />
                      <div>
                        <h5 className="mb-1">{movie.title}</h5>
                        <p className="mb-0">
                          <strong>Rating:</strong> {movie.rating}/10
                        </p>
                      </div>
                    </div>
                    {/* Remove Button: Only show if not a guest */}
                    {!isGuest && (
                      <Button
                        variant="danger"
                        onClick={() =>
                          console.log(
                            `Remove functionality is disabled for guests.`
                          )
                        }
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                </ListGroup.Item>
              ))}
            </ListGroup>
          </Card>
        ) : (
          <div className="text-center">
            <p>No movies found in this watchlist.</p>
            <Button variant="primary" onClick={() => navigate("/")}>
              Find Movies
            </Button>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default WatchListView;
