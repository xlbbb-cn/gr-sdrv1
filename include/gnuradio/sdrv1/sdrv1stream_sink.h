/* -*- c++ -*- */
/*
 * Copyright 2025 leonard.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SDRV1_SDRV1STREAM_SINK_H
#define INCLUDED_SDRV1_SDRV1STREAM_SINK_H

#include <gnuradio/sdrv1/api.h>
#include <gnuradio/sync_block.h>

#include <string>

namespace gr {
  namespace sdrv1 {

    /*!
     * \brief <+description of block+>
     * \ingroup sdrv1
     *
     */
    class SDRV1_API sdrv1stream_sink : virtual public gr::sync_block
    {
     public:
      typedef std::shared_ptr<sdrv1stream_sink> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of sdrv1::sdrv1stream_sink.
       *
       * To avoid accidental use of raw pointers, sdrv1::sdrv1stream_sink's
       * constructor is in a private implementation
       * class. sdrv1::sdrv1stream_sink::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& ip_addr,
                       const std::string& chn,
                       int32_t bufsize);
    };

  } // namespace sdrv1
} // namespace gr

#endif /* INCLUDED_SDRV1_SDRV1STREAM_SINK_H */
 