// HokieFind listing + claim components

function ListingRow({ item, onEdit, onDelete, onClaim, onViewClaims, showActions = "public" }) {
  return (
    <div className="hf-listing">
      <div className="hf-listing-photo">
        {item.photo ? <img src={item.photo} style={{width:"100%",height:"100%",objectFit:"cover"}}/> : "PHOTO"}
      </div>
      <div className="hf-listing-body">
        <div className="hf-listing-head">
          <div style={{flex:1, minWidth:0}}>
            <h3 className="hf-listing-title">{item.title}</h3>
            <p className="hf-listing-desc">{item.description}</p>
            <div className="hf-listing-meta">
              <span>📍 {item.location}</span>
              <span className="mono">{item.date}</span>
            </div>
          </div>
          <Badge kind={item.status || "active"}>
            {item.status === "returned" ? "Returned"
              : item.status === "pending" ? "Pending"
              : "Active"}
          </Badge>
        </div>
        <div className="hf-listing-actions">
          {showActions === "owner" && <>
            <a onClick={onEdit}>Edit</a>
            <a onClick={onDelete}>Delete</a>
          </>}
          {showActions === "public" && <>
            <a className="claim" onClick={onClaim}>Claim →</a>
            <a onClick={onViewClaims}>View Claims</a>
          </>}
        </div>
      </div>
    </div>
  );
}

function ClaimRow({ claim }) {
  return (
    <div className="hf-listing" style={{alignItems:"flex-start"}}>
      <div className="hf-listing-body">
        <div className="hf-listing-head">
          <div>
            <h3 className="hf-listing-title">{claim.firstName} {claim.lastName}</h3>
            <p className="hf-listing-desc">{claim.message}</p>
            <div className="hf-listing-meta">
              <span className="mono">{claim.date}</span>
              <span>on <strong style={{color:"var(--fg-primary)"}}>{claim.itemTitle}</strong></span>
            </div>
          </div>
          <Badge kind={claim.status || "pending"}>
            {claim.status === "returned" ? "Approved" : "Pending"}
          </Badge>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { ListingRow, ClaimRow });
